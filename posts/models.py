from django.contrib.auth.models import User
from django.db import models

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    content = models.TextField(verbose_name='Текст поста')
    image = models.ImageField(upload_to='posts_image/',blank=True,null=True,verbose_name='Картинка',)
    views_count = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True, verbose_name='Лайки')
    def __str__(self):
        return (
            f'{self.author.username} - {self.created_at.strftime("%d.%m.%Y %H:%M")}'
        )

    class Meta:
        ordering = ['-created_at']

class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views', verbose_name='Пост')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_views', verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата просмотра')

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"@{self.user.username} посмотрел пост #{self.post.id}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор')
    content = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    def __str__(self):
        return f'Комментарий от {self.author.username} к посту {self.post.pk}'

    class Meta:
        ordering = ['created_at']