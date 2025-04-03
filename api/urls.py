from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterAPIview.as_view()),
    path("login/", views.LoginAPIview.as_view()),
    path("logout/", views.LogoutAPIView.as_view()),
    # Profile
    path("user/profile/", views.UserProfileGenericView.as_view()),
    path("user/profile/<str:id>/", views.GetUserProfileGenericView.as_view()),
    # Follow request
    path("user/profile/<str:id>/follow/", views.FollowProfile.as_view()),
    path("user/profile/<str:id>/following/", views.FollowingProfile.as_view()),
    # Search User
    path("user/search/", views.SearchUserAPIview.as_view()),
    # Post
    path("user/posts/", views.PostGenericView.as_view()),
    path("user/posts/<str:id>/", views.PostGenericView.as_view()),
    path("post/<str:id>/like/", views.PostLikedAPIview.as_view()),
    # Home
    path("user/home/", views.GetPostByFollower.as_view()),
    path("user/liked/post/", views.getLikedPost.as_view()),
]
