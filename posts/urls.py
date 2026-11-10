from django.urls import path
from .views import feed_view,edit_post_view, like_post, create_post_view,add_comment, edit_comment_view,delete_comment, delete_post

urlpatterns = [
    path('', feed_view, name='feed'),
    path('post/<int:pk>/like/', like_post, name='like_post'),
    path('post/<int:pk>/delete/', delete_post, name='delete_post'),
    path('post/<int:pk>/comment/', add_comment, name='add_comment'),
    path('post/create/', create_post_view, name='create_post'),
    path('comment/<int:pk>/delete/', delete_comment, name='delete_comment'),
    path('post/<int:pk>/edit/', edit_post_view, name='edit_post'),
    path('comment/<int:pk>/edit/', edit_comment_view, name='edit_comment'),
]