from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()


class JWTRefreshMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """Checks tokens before processing the request."""
        request.user = None  # Reset user before processing

        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if not access_token and not refresh_token:
            return  # No token, continue request
        if not access_token:
            try:

                access_token_obj = AccessToken(access_token)
                request.user = User.objects.get(id=access_token_obj["user_id"])

            except Exception:
                if not refresh_token:
                    return  # No refresh token, continue without authentication

                try:
                    # ✅ Refresh access & refresh tokens
                    new_access_token, new_refresh_token = self.refresh_access_token(
                        refresh_token
                    )

                    # ✅ Attach new tokens to request (so process_response can set cookies)
                    request.new_access_token = new_access_token
                    request.new_refresh_token = new_refresh_token

                    # ✅ Authenticate user
                    access_token_obj = AccessToken(new_access_token)
                    request.user = User.objects.get(id=access_token_obj["user_id"])

                except Exception:
                    return JsonResponse(
                        {"detail": "Authentication failed. Please log in again."},
                        status=401,
                    )

    def process_response(self, request, response):
        """Sets new tokens in cookies if refreshed."""
        if hasattr(request, "new_access_token") and hasattr(
            request, "new_refresh_token"
        ):
            response.set_cookie(
                "access_token",
                request.new_access_token,
                max_age=900,  # 15 minutes
                httponly=True,
                secure=True,
                samesite="None",
            )
            response.set_cookie(
                "refresh_token",
                request.new_refresh_token,
                max_age=604800,  # 7 days
                httponly=True,
                secure=True,
                samesite="None",
            )
        return response  # ✅ Ensure updated response is returned

    def refresh_access_token(self, refresh_token):
        """Tries to refresh the access token using the refresh token"""
        refresh = RefreshToken(refresh_token)
        user_id = refresh.payload.get("user_id")

        if not user_id:
            raise Exception("Invalid refresh token")

        user = User.objects.get(id=user_id)
        new_refresh_token = RefreshToken.for_user(user)  # Generate new refresh token
        return str(new_refresh_token.access_token), str(new_refresh_token)
