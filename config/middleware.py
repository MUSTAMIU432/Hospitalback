from apps.users.jwt_utils import get_user_from_token


class JWTAuthenticationMiddleware:
    """Attach request.user from Bearer JWT when valid (after session auth)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Bearer "):
            token = auth[7:].strip()
            user = get_user_from_token(token)
            if user is not None:
                request.user = user
        response = self.get_response(request)
        return response
