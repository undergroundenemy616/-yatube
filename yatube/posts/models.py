from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)
    image = models.ImageField(upload_to='posts/', null=True)
    comment_count = models.IntegerField(null=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField("date published", auto_now_add=True)

    def __str__(self):
        return self.title


class Follow(models.Model):
    user = models.ForeignKey(User, related_name="follower", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)

    class Meta:
        unique_together = [["user", "author"]]

    def __str__(self):
        return self.title