from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()


class JWTAuthenticationFromCookie(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get("access_token")  # Get access token from cookies
        refresh_token = request.COOKIES.get("refresh_token")  # Get refresh token
        # print('token ===>',token)
        # print('refresh_token ===>',refresh_token)
        try:
            access_token = AccessToken(token)

            user = User.objects.get(id=access_token["user_id"])

            return (user, None)

        except Exception as e:
            if refresh_token:
                try:
                    new_access_token, new_refresh_token = self.refresh_access_token(
                        refresh_token
                    )

                    # Authenticate the user with the new token
                    access_token = AccessToken(new_access_token)

                    user_id = access_token["user_id"]
                    user = User.objects.get(id=user_id)

                    return (user, None)

                except Exception as e:
                    print(e)
                    # raise AuthenticationFailed("Token expired. Please log in again.")
                    return None
            print("yes")
            # raise AuthenticationFailed({"detail":"You are not logged in! please log in to get access"})
            return None

    def refresh_access_token(self, refresh_token):
        """Tries to refresh the access token using the refresh token"""
        refresh = RefreshToken(refresh_token)
        user_id = refresh.payload.get("user_id")
        user = User.objects.get(id=user_id)
        new_access_token = str(refresh.access_token)
        new_refresh_token = str(RefreshToken.for_user(user))
        return new_access_token, new_refresh_token
