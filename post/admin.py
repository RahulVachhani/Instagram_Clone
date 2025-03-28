from django.contrib import admin

from .models import Like, Post

# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "profile"]


@admin.register(Like)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "post", "profile"]
