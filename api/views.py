from django.contrib.auth import get_user_model
from django.utils.timezone import timedelta

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from post.models import Like, Post
from users.models import Follower, Profile

from .serializers import (
    LoginSerializer,
    PostSerializers,
    UserHomePostSerializers,
    UserProfileFollowerSerializer,
    UserProfileSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterAPIview(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            return Response(
                {"message": "User created successfully", "user": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIview(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh_token = RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
            response = Response(
                {
                    "message": "login successfully",
                    "data": {
                        "refresh_token": str(refresh_token),
                        "access_token": access_token,
                    },
                },
                status=status.HTTP_200_OK,
            )

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                max_age=timedelta(days=7),  # Expiry time for refresh token
                httponly=True,  # HttpOnly flag for security
                secure=True,  # Set this to True in production (requires HTTPS)
                samesite="None",  # Allows cross-site cookies (if required)
            )

            response.set_cookie(
                key="access_token",
                value=access_token,
                max_age=timedelta(
                    minutes=15
                ),  # Expiry time for access token (shorter lifespan)
                httponly=True,  # HttpOnly flag for security
                secure=True,  # Set this to True in production (requires HTTPS)
                samesite="None",  # Allows cross-site cookies (if required)
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        response = Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class UserProfileGenericView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class GetUserProfileGenericView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    lookup_field = "id"


class FollowProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        following_user_profile = Profile.objects.filter(id=id)

        if not following_user_profile.exists():
            return Response(
                {"user": [f"The following user is not found with given id {id}"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        followers = Follower.objects.filter(
            following=following_user_profile.first()
        ).select_related("follower")

        follower_profiles = [f.follower for f in followers]

        serializer = UserProfileFollowerSerializer(follower_profiles, many=True)
        return Response(
            {"follower_count": followers.count(), "follower": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request, id):
        follower_user_profile = request.user.profile
        following_user_profile = Profile.objects.filter(id=id)
        if not following_user_profile.exists():
            return Response(
                {"user": [f"The following user is not found with given id {id}"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        following_user_profile = following_user_profile.first()
        if follower_user_profile.id == int(id):
            return Response(
                {"message": ["User can not follow yourself"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follower = Follower.objects.filter(
            follower=follower_user_profile, following=following_user_profile
        )

        if follower.exists():
            return Response(
                {"message": ["user has already following that profile"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            Follower.objects.create(
                follower=follower_user_profile, following=following_user_profile
            )
        except Exception:
            return Response(
                {"error": ["Something went wrong when creating a follow request"]}
            )

        return Response({"message": "Successfully follow"}, status=status.HTTP_200_OK)

    def delete(self, request, id):
        follower_user_profile = request.user.profile
        following_user_profile = Profile.objects.filter(id=id)

        if not following_user_profile.exists():
            return Response(
                {"user": [f"The following user is not found with given id {id}"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        following_user_profile = following_user_profile.first()

        if follower_user_profile.id == int(id):
            return Response(
                {"message": ["User can not follow/unfollow yourself"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follower = Follower.objects.filter(
            follower=follower_user_profile, following=following_user_profile
        )

        if follower.exists():
            follower.delete()
            return Response(
                {"message": ["Successfully unfollow that profile"]},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": ["User can not follow that profile"]},
            status=status.HTTP_400_BAD_REQUEST,
        )


class FollowingProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user_profile = Profile.objects.filter(id=id)
        if not user_profile.exists():
            return Response(
                {"user": [f"The following user is not found with given id {id}"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        following = Follower.objects.filter(
            follower=user_profile.first()
        ).select_related("following")
        following_profiles = [f.following for f in following]
        serializer = UserProfileFollowerSerializer(following_profiles, many=True)
        return Response(
            {"following_count": following.count(), "following_users": serializer.data},
            status=status.HTTP_200_OK,
        )


class SearchUserAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get("query")
        user = User.objects.filter(username__icontains=query).prefetch_related(
            "profile"
        )
        if not user.exists():
            return Response(
                {"message": "user is not found"}, status=status.HTTP_404_NOT_FOUND
            )

        profile = [u.profile for u in user]
        serializer = UserProfileSerializer(profile, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostGenericView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializers

    def get_queryset(self):
        profile_id = self.kwargs.get("id")
        if profile_id:
            return Post.objects.filter(profile__id=profile_id)
        """Retrieve only the posts created by the logged-in user."""
        return Post.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(profile=profile)


class GetPostByFollower(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        following_profiles = request.user.profile.following_users.all()
        follower_profiles = [f.following for f in following_profiles]
        posts = sorted(
            [p for f in follower_profiles for p in f.posts.all()],
            key=lambda post: post.created_at,
            reverse=True,  # Descending order (latest first)
        )

        serializer = UserHomePostSerializers(
            posts, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostLikedAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        post = Post.objects.filter(id=id)
        if not post.exists():
            return Response(
                {"message": ["post not found"]}, status=status.HTTP_404_NOT_FOUND
            )
        post = post.first()
        liked, created = Like.objects.get_or_create(
            post=post, profile=request.user.profile
        )
        if not created:
            liked.delete()
            return Response(
                {"message": ["successfully unlike post"]}, status=status.HTTP_200_OK
            )
        return Response(
            {"message": ["successfully like post"]}, status=status.HTTP_200_OK
        )


class getLikedPost(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = request.user.profile
        liked_Post = Like.objects.filter(profile=user_profile).select_related("post")
        liked_Posts = [post.post for post in liked_Post]
        serializers = PostSerializers(liked_Posts, many=True)
        return Response(
            {
                "message": "Successfully Retrived Liked Posts",
                "total count": len(liked_Posts),
                "posts": serializers.data,
            },
            status=status.HTTP_200_OK,
        )
