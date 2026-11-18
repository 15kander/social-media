from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User

from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.db.models import Q, Count
from posts.models import Post, Comment
from users.models import Block


def admin_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)





@user_passes_test(admin_check)
def admin_dashboard(request):
    # Считаем регистрации за последние 7 дней
    today = timezone.now().date()
    start_date = today - timedelta(days=6)

    daily_regs = User.objects.filter(date_joined__date__gte=start_date) \
        .annotate(date=TruncDate('date_joined')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')

    # Формируем списки для графика (чтобы заполнить нулями дни без регистраций)
    chart_labels = []
    chart_data = []
    for i in range(7):
        d = start_date + timedelta(days=i)
        matching = next((item for item in daily_regs if item['date'] == d), None)
        count = matching['count'] if matching else 0
        chart_labels.append(d.strftime('%d.%m'))
        chart_data.append(count)

    context = {
        'total_users': User.objects.count(),
        'total_posts': Post.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_blocks': Block.objects.count(),
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@user_passes_test(admin_check)
def admin_users_list(request):
    """Список пользователей с поддержкой поиска"""
    query = request.GET.get('q', '').strip()
    users = User.objects.all()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    users = users.order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users, 'query': query})


@user_passes_test(admin_check)
def admin_edit_user(request, user_id):
    """Редактирование данных пользователя и профиля"""
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        target_user.username = request.POST.get('username')
        target_user.email = request.POST.get('email')
        target_user.is_staff = 'is_staff' in request.POST
        target_user.save()

        profile = target_user.profile
        profile.bio = request.POST.get('bio', '')
        profile.is_private = 'is_private' in request.POST
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()

        return redirect('admin_users')
    return render(request, 'admin_panel/edit_user.html', {'target_user': target_user})


@user_passes_test(admin_check)
def admin_delete_user(request, user_id):
    """Удаление пользователя"""
    user_to_delete = get_object_or_404(User, id=user_id)
    if user_to_delete != request.user:
        user_to_delete.delete()
    return redirect('admin_users')


@user_passes_test(admin_check)
def admin_posts_list(request):
    """Управление постами с поддержкой поиска"""
    query = request.GET.get('q', '').strip()
    posts = Post.objects.all()
    if query:
        posts = posts.filter(Q(content__icontains=query) | Q(author__username__icontains=query))
    posts = posts.order_by('-created_at')
    return render(request, 'admin_panel/posts.html', {'posts': posts, 'query': query})


@user_passes_test(admin_check)
def admin_edit_post(request, post_id):
    """Редактирование поста"""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.content = request.POST.get('content')
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        post.save()
        return redirect('admin_posts')
    return render(request, 'admin_panel/edit_post.html', {'post': post})


@user_passes_test(admin_check)
def admin_delete_post(request, post_id):
    """Удаление поста"""
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('admin_posts')


@user_passes_test(admin_check)
def admin_comments_list(request):
    """Модерация комментариев"""
    comments = Comment.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/comments.html', {'comments': comments})


@user_passes_test(admin_check)
def admin_delete_comment(request, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return redirect('admin_comments')


@user_passes_test(admin_check)
def admin_blocks_list(request):
    """Мониторинг блокировок"""
    blocks = Block.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/blocks.html', {'blocks': blocks})


@user_passes_test(admin_check)
def admin_delete_block(request, block_id):
    """Снятие блокировки"""
    block = get_object_or_404(Block, id=block_id)
    block.delete()
    return redirect('admin_blocks')