from .models import Post
from django.forms import ModelForm


class PostFrom(ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text")
        required = {
            "group": False,
        }
        labels = {
            "group": "Сообщества",
            "text": "Текст записи"
        }
