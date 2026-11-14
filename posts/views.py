from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from users.models import Block, Follow, Notification
from .forms import CommentForm, PostForm
from .models import Comment, Post


def get_blocked_users_ids(user):
  if not user.is_authenticated:
    return []
  blocks = Block.objects.filter(Q(blocker=user) | Q(blocked=user))
  blocked_ids = set()
  for b in blocks:
    blocked_ids.add(b.blocker_id)
    blocked_ids.add(b.blocked_id)
  blocked_ids.discard(user.id)
  return list(blocked_ids)


@login_required
def create_post_view(request):
  if request.method == 'POST':
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
      post = form.save(commit=False)
      post.author = request.user
      post.save()
      return redirect('feed')
  else:
    form = PostForm()

  return render(request, 'posts/create_post.html', {'form': form})


def feed_view(request):
  if request.method == 'POST' and 'comment_form_submit' in request.POST:
    comment_form = CommentForm(request.POST)
    post_id = request.POST.get('post_id')
    post_instance = get_object_or_404(Post, pk=post_id)

    if (
        request.user.is_authenticated
        and post_instance.author_id in get_blocked_users_ids(request.user)
    ):
      return redirect('feed')

    if comment_form.is_valid():
      comment = comment_form.save(commit=False)
      comment.author = request.user
      comment.post = post_instance
      comment.save()

      if request.user != post_instance.author:
        Notification.objects.create(
            recipient=post_instance.author,
            sender=request.user,
            notification_type='comment',
            post=post_instance,
            text = comment.content

        )
      return redirect('feed')

  comment_form = CommentForm()
  feed_type = request.GET.get('feed', 'all')

  excluded_users = (
      get_blocked_users_ids(request.user) if request.user.is_authenticated else []
  )

  if feed_type == 'following' and request.user.is_authenticated:
    following_users = Follow.objects.filter(follower=request.user).values_list(
        'following', flat=True
    )
    posts = (
        Post.objects.filter(author__in=following_users)
        .exclude(author__id__in=excluded_users)
        .order_by('-created_at')
    )
  else:
    posts = (
        Post.objects.exclude(author__id__in=excluded_users).order_by(
            '-created_at'
        )
    )

  context = {
      'posts': posts,
      'comment_form': comment_form,
      'active_feed': feed_type,
  }
  if request.headers.get('x-requested-with') == 'XMLHttpRequest':
    html = render_to_string(
        'posts/partials/posts_list.html', context, request=request
    )
    return HttpResponse(html)
  return render(request, 'posts/feed.html', context)


@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

        # Уведомление автору (если лайкнул не свой пост)
        if request.user != post.author:
            Notification.objects.get_or_create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post
            )

    # Если запрос пришел через AJAX (fetch), возвращаем JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes.count()
        })

    # На всякий случай для обычных запросов
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

@login_required
def delete_post(request, pk):
  post = get_object_or_404(Post, pk=pk)
  if post.author == request.user or request.user.is_superuser:
    post.delete()
  return redirect('feed')


def add_comment(request, pk):
  if not request.user.is_authenticated:
    return redirect('login')

  post = get_object_or_404(Post, pk=pk)

  if request.method == 'POST':
    content = request.POST.get('content', '').strip()
    if content:
      Comment.objects.create(post=post, author=request.user, content=content)

      if request.user != post.author:
        Notification.objects.create(
            recipient=post.author,
            sender=request.user,
            notification_type='comment',
            post=post,
            text=content
        )

  return redirect(request.META.get('HTTP_REFERER', 'feed'))


@login_required
def delete_comment(request, pk):
  comment = get_object_or_404(Comment, pk=pk)
  if comment.author == request.user or request.user.is_superuser:
    comment.delete()
  return redirect('feed')

@login_required
def edit_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('feed')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('feed')
    else:
        form = PostForm(instance=post)

    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})

@login_required
def edit_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        return redirect('feed')
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('feed')
    else:
        form = CommentForm(instance=comment)
    return render(request, 'posts/edit_comment.html', {'form': form, 'comment': comment})