from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class ApiKeyAuthentication(BaseAuthentication):
    """
    Authenticate via ``Authorization: Api-Key <key>`` header.

    Falls through (returns None) when the header is absent or uses a different
    scheme, allowing other backends (JWT, session) to handle the request.
    """

    HEADER_PREFIX = "Api-Key"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith(self.HEADER_PREFIX + " "):
            return None

        raw_key = auth_header[len(self.HEADER_PREFIX) + 1:]
        if not raw_key:
            raise AuthenticationFailed("API key is missing")

        from app.models.api_key import ApiKey

        hashed = ApiKey.hash_key(raw_key)

        try:
            api_key = ApiKey.objects.select_related("user").get(hashed_key=hashed)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key")

        if not api_key.user.is_active:
            raise AuthenticationFailed("User account is disabled")

        ApiKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())

        return (api_key.user, api_key)

    def authenticate_header(self, request):
        return self.HEADER_PREFIX


class ApiKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    """Registers ApiKeyAuthentication with drf-spectacular's OpenAPI schema generation."""

    target_class = "app.middleware.api_key_authentication.ApiKeyAuthentication"
    name = "ApiKeyAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "API key authentication. Enter: Api-Key <your_key>",
        }
