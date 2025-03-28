from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, db_collation="utf8_bin")
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username


class Profile(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to="profile/images", default="profile/images/default.jpeg"
    )
    bio = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, default="male")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following_users.count()

    @property
    def posts_count(self):
        return self.posts.count()

    def __str__(self):
        return f"{self.user}"


class Follower(models.Model):
    follower = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="following_users"
    )  # Who is following
    following = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="followers"
    )  # Who is being followed
    created_at = models.DateTimeField(auto_now_add=True)  # Track follow time

    class Meta:
        unique_together = ("follower", "following")  # Prevent duplicate follows
        indexes = [
            models.Index(fields=["follower", "following"])
        ]  # Index for faster lookups

    def __str__(self):
        return f"{self.follower} follows {self.following}"
