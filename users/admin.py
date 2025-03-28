from django.contrib import admin

from .models import Follower, Profile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email"]


@admin.register(Profile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user"]


@admin.register(Follower)
class UserProfileFollowerAdmin(admin.ModelAdmin):
    list_display = ["id", "follower__user__username", "following__user__username"]
