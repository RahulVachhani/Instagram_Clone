from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOrUsernameAuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either their username or email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Check if the input is an email or a username
        user = None
        if "@" in username:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        # Check if the password is correct
        if user and user.check_password(password):
            return user

        return None
