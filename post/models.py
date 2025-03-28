from django.db import models

from users.models import Profile


class Post(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    image = models.ImageField(upload_to="profile/images")
    description = models.TextField(blank=True, null=True)
    likes = models.ManyToManyField(Profile, related_name="liked_posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.profile.user.username} {self.likes.count()}"
