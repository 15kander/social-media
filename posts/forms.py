from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):

  class Meta:
    model = Post
    fields = ['content', 'image']
    widgets = {
        'content': forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Что у вас нового?',
            }
        ),
        'image': forms.FileInput(attrs={'class': 'form-control mt-2'}),
    }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 2,
                    'placeholder': 'Написать комментарий...',
                }
            )
        }