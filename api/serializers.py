from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import serializers

from users.models import Profile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError({"error": "Invalid credentials"})
        user.last_login = timezone.now()
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    posts_count = serializers.IntegerField(read_only=True)
    follower_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "image",
            "bio",
            "gender",
            "posts_count",
            "follower_count",
            "following_count",
            "is_following",
        ]

    def update(self, instance, validated_data):

        user_data = validated_data.pop("user", {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)

        instance.save()
        user.save()
        return instance

    def get_is_following(self, obj):
        """Check if the authenticated user follows this profile"""
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            if obj.user == request.user:
                return None
            return obj.followers.filter(follower__user=request.user).exists()
        return False

    def to_representation(self, instance):
        """Dynamically remove 'is_following' if user is viewing their own profile"""
        data = super().to_representation(instance)
        request = self.context.get("request")
        # print(request)
        if request is not None:
            if (
                request
                and request.user.is_authenticated
                and instance.user == request.user
            ):
                data.pop("is_following", None)
        return data


class UserProfileFollowerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = Profile
        fields = ["id", "username", "email", "first_name", "last_name", "image"]
