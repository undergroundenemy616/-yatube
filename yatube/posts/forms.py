from .models import Post, Comment
from django.forms import ModelForm


class PostFrom(ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text", "image")
        required = {
            "group": False,
        }
        labels = {
            "group": "Сообщества",
            "text": "Текст записи"
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
