from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

from posts.views import get_blocked_users_ids
from .context_processors import unread_counts
from .models import Profile, Follow, Message, Notification, Block
from .forms import UserUpdateForm, ProfileUpdateForm
from django.http import Http404

def check_block_relation(user1,user2):
    if not user1.is_authenticated or not user2.is_authenticated:
        return False
    return Block.objects.filter(
        Q(blocker=user1, blocked=user2) | Q(blocker=user2, blocked=user1)
    ).exists()

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)

    they_blocked_us = Block.objects.filter(blocker=profile_user, blocked=request.user).exists() if request.user.is_authenticated else False
    if they_blocked_us:
        raise Http404("Пользователь не найден")

    profile, created = Profile.objects.get_or_create(user=profile_user)
    is_following = False
    follow_request_sent = False
    can_view_posts = False
    pending_requests = []
    if request.user.is_authenticated and request.user == profile_user:
        pending_requests = Follow.objects.filter(following=request.user, is_approved=False)
    if not profile.is_private:
        can_view_posts = True
    if request.user.is_authenticated:
        if request.user == profile_user:
            can_view_posts = True
        else:
            follow_obj = Follow.objects.filter(follower=request.user, following=profile_user).first()
            if follow_obj:
                if follow_obj.is_approved:
                    is_following = True
                    can_view_posts = True
                else:
                    follow_request_sent=True
    posts = profile_user.post_set.all().order_by('-created_at') if can_view_posts else []
    is_blocked = Block.objects.filter(blocker=request.user, blocked=profile_user).exists() if request.user.is_authenticated else False
    followers_count = profile_user.followers_set.count()
    following_count = profile_user.following_set.count()

    context = {
        'profile_user': profile_user,
        'profile':profile,
        'posts': posts,
        'is_blocked':is_blocked,
        'is_following': is_following,
        'follow_request_sent': follow_request_sent,
        'can_view_posts': can_view_posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'pending_requests':pending_requests,
    }
    return render(request, 'profile.html', context)

@login_required
def toggle_privacy(request):
    if request.method == 'POST':
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.is_private = not profile.is_private
        profile.save()
    return redirect('profile',username=request.user.username)


@login_required
def accept_follow(request, username):
    follower_user = get_object_or_404(User, username=username)
    follow_obj = get_object_or_404(Follow, follower=follower_user, following=request.user, is_approved=False)
    follow_obj.is_approved = True
    follow_obj.save()
    Notification.objects.create(
        recipient=follower_user,
        sender=request.user,
        notification_type='follow_accepted'
    )
    return redirect('profile', username=request.user.username)

@login_required
def reject_follow(request, username):
    follower_user = get_object_or_404(User, username=username)
    follow_obj = get_object_or_404(Follow, follower=follower_user, following=request.user, is_approved=False)
    follow_obj.delete()
    return redirect('profile', username=request.user.username)

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'edit_profile.html', context)


def search_users(request):
    query = request.GET.get('q', '')
    users = []
    if query and request.user.is_authenticated:
        excluded_users = get_blocked_users_ids(request.user)
        excluded_users.append(request.user.id)
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id)

    return render(request, 'search.html', {'users': users, 'query': query})


def toggle_follow(request, username):
    if not request.user.is_authenticated:
        return redirect('login')

    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        return redirect('profile', username=username)

    if Block.objects.filter(
            Q(blocker=request.user, blocked=profile_user) | Q(blocker=profile_user, blocked=request.user)).exists():
        return redirect('profile', username=username)

    existing_follow = Follow.objects.filter(follower=request.user, following=profile_user).first()

    if not existing_follow:
        profile, _ = Profile.objects.get_or_create(user=profile_user)
        is_approved = not profile.is_private

        Follow.objects.create(follower=request.user, following=profile_user, is_approved=is_approved)
        Notification.objects.create(
            recipient=profile_user,
            sender=request.user,
            notification_type='follow'
        )
    else:
        existing_follow.delete()

    return redirect('profile', username=username)

@login_required
def followers_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    if Block.objects.filter(blocker=profile_user, blocked=request.user).exists():
        raise Http404("Пользователь не найден")
    profile,_=Profile.objects.get_or_create(user=profile_user)
    is_approved_follower = Follow.objects.filter(follower=request.user, following=profile_user,is_approved=True).exists()
    can_view = not profile.is_private or request.user == profile_user or is_approved_follower
    if not can_view:
        return redirect('profile',username=username)
    followers = [f.follower for f in profile_user.followers_set.filter(is_approved=True)]

    context = {
        'profile_user': profile_user,
        'users_list': followers,
        'page_type': 'followers',
    }
    return render(request, 'user_list.html', context)

@login_required
def following_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    if Block.objects.filter(blocker=profile_user, blocked=request.user).exists():
        raise Http404("Пользователь не найден")
    profile, _ = Profile.objects.get_or_create(user=profile_user)

    is_approved_follower = Follow.objects.filter(follower=request.user, following=profile_user,is_approved=True).exists()
    can_view = not profile.is_private or request.user == profile_user or is_approved_follower
    if not can_view:
        return redirect('profile',username=username)
    following = [f.following for f in profile_user.following_set.filter(is_approved=True)]

    context = {
        'profile_user': profile_user,
        'users_list': following,
        'page_type': 'following',
    }
    return render(request, 'user_list.html', context)


def inbox_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    messages_qs = Message.objects.filter(Q(sender=request.user) | Q(recipient=request.user))

    chat_partners = set()
    for msg in messages_qs:
        if msg.sender != request.user:
            chat_partners.add(msg.sender)
        if msg.recipient != request.user:
            chat_partners.add(msg.recipient)
    chats_data = []
    for partner in chat_partners:
        unread_count = Message.objects.filter(sender=partner, recipient=request.user, is_read=False).count()
        chats_data.append({'user':partner, 'unread_count':unread_count})
    context = {
        'chats_data': chats_data,
    }
    return render(request, 'inbox.html', context)


def chat_view(request, username):
    if not request.user.is_authenticated:
        return redirect('login')

    other_user = get_object_or_404(User, username=username)

    # Проверяем, есть ли блокировка в любую сторону
    block_record = Block.objects.filter(
        Q(blocker=request.user, blocked=other_user) |
        Q(blocker=other_user, blocked=request.user)
    ).first()

    is_blocked = block_record is not None
    i_blocked_them = block_record and block_record.blocker == request.user

    # Если отправляется сообщение, но стоит блокировка — прерываем отправку
    if request.method == 'POST':
        if is_blocked:
            return redirect('chat_detail', username=username)

        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                content=content
            )
            Notification.objects.create(
                recipient=other_user,
                sender=request.user,
                notification_type='message'
            )
            return redirect('chat_detail', username=other_user.username)

    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('created_at')

    Message.objects.filter(sender=other_user, recipient=request.user, is_read=False).update(is_read=True)

    context = {
        'other_user': other_user,
        'messages': messages,
        'is_blocked': is_blocked,
        'i_blocked_them': i_blocked_them,
    }
    return render(request, 'chat_detail.html', context)


def notifications_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    notifications = request.user.notifications.all().order_by('-created_at')
    notifications.filter(is_read=False).update(is_read=True)

    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications.html', context)

def toggle_block(request, username):
    if not request.user.is_authenticated:
        return redirect('login')
    target_user = get_object_or_404(User, username=username)
    if request.user == target_user:
        return redirect('profile', username=username)

    existing_block = Block.objects.filter(blocker=request.user, blocked=target_user).first()
    if not existing_block:
        Block.objects.create(blocker=request.user, blocked=target_user)
        Follow.objects.filter(follower=request.user, following=target_user).delete()
        Follow.objects.filter(follower=target_user, following=request.user).delete()
    else:
        existing_block.delete()
    return redirect('profile', username=username)