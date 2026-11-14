from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from posts.models import Post


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg', blank=True, null=True, verbose_name="Аватар")
    is_private = models.BooleanField(default=False)
    def __str__(self):
        return f'Профиль {self.user.username}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set',verbose_name='Кто подписывается',)
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set', verbose_name='На кого подписывается',)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('follower', 'following'),)

    def __str__(self):
        return f'{self.follower.username} -> {self.following.username} (approved: {self.is_approved})'

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'От @{self.sender.username} к @{self.recipient.username}: {self.content[:20]}'

class Notification(models.Model):
    NOTIFICATION_TYPES = (('follow', 'подписался на вас'), ('like', 'оценил ваш пост'), ('message', 'прислал сообщение'),('comment', 'оставил комментарий'),('follow_accepted','Подписка одобрена'))
    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey('posts.Post', related_name='notifications', on_delete=models.CASCADE,null=True, blank=True)
    text = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Уведомление для @{self.recipient.username} от @{self.sender.username} ({self.notification_type})'

class Block(models.Model):
    blocker = models.ForeignKey(User, related_name='blocking', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f'@{self.blocker.username} заблокировал @{self.blocked.username}'