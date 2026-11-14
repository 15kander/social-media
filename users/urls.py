from django.urls import path
from .views import (
    register_view,
    notifications_view,
    search_users,
    followers_view,
    following_view,
    edit_profile,
    profile_view,
    toggle_follow,
    inbox_view,
    chat_view,
    toggle_block,
    toggle_privacy,
    accept_follow,
    reject_follow,
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('notifications/', notifications_view, name='notifications'),
    path('search/', search_users, name='user_search'),
    path('inbox/', inbox_view, name='inbox'),
    path('profile/toggle-privacy/', toggle_privacy, name='toggle_privacy'),
    path('chat/<str:username>/', chat_view, name='chat_detail'),
    path('profile/<str:username>/', profile_view, name='profile'),
    path('profile/accept/<str:username>/', accept_follow, name='accept_follow'),
    path('profile/reject/<str:username>/', reject_follow, name='reject_follow'),
    path('profile/<str:username>/followers/', followers_view, name='followers_list'),
    path('profile/<str:username>/following/', following_view, name='following_list'),
    path('profile/<str:username>/follow', toggle_follow, name='toggle_follow'),
    path('profile/<str:username>/block/', toggle_block, name='toggle_block'),
]