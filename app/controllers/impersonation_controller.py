from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter

from app.actions.action import Action
from app.handlers.impersonation_handler import ImpersonationHandler
from app.handlers.api_handler import ApiHandler
from app.utils.throttling import AnonRateThrottle, UserRateThrottle
from app.models.user import User


class ImpersonateUserSerializer(serializers.Serializer):
    user_uuid = serializers.UUIDField(help_text="UUID of the user to impersonate")


@extend_schema(
    summary="Start impersonation",
    parameters=[],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "user_uuid": {
                    "type": "string",
                    "format": "uuid",
                    "description": "UUID of the user to impersonate",
                }
            },
            "required": ["user_uuid"],
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "output": {
                    "type": "boolean",
                    "description": "True if impersonation started successfully",
                },
                "error": {"type": "boolean", "description": "False if successful"},
                "http_response_code": {
                    "type": "integer",
                    "description": "HTTP status code",
                },
                "error_messages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Error messages if any",
                },
            },
        },
        400: {
            "type": "object",
            "properties": {
                "output": {"type": "null"},
                "error": {"type": "boolean"},
                "http_response_code": {"type": "integer"},
                "error_messages": {"type": "array", "items": {"type": "string"}},
            },
        },
        403: {
            "type": "object",
            "properties": {
                "output": {"type": "null"},
                "error": {"type": "boolean"},
                "http_response_code": {"type": "integer"},
                "error_messages": {"type": "array", "items": {"type": "string"}},
            },
        },
        404: {
            "type": "object",
            "properties": {
                "output": {"type": "null"},
                "error": {"type": "boolean"},
                "http_response_code": {"type": "integer"},
                "error_messages": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    examples=[],
    description=(
        "Start impersonating a target user (admin/staff only). "
        "On success, the controller stores the impersonated user UUID in the session for subsequent requests."
    ),
)
@api_view(["POST"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def start_impersonation(request):
    """
    Start impersonating a user.

    Only admin or staff users can impersonate other users.
    The impersonated user will be available as request.impersonated_user
    in subsequent requests.
    """
    # Validate request data
    serializer = ImpersonateUserSerializer(data=request.data)
    if not serializer.is_valid():
        return Action().bad_request(serializer.errors).json_response()

    user_uuid = serializer.validated_data["user_uuid"]

    # Call handler first to validate
    result = ImpersonationHandler.start_impersonation(request.user, user_uuid)

    # Only store in session if successful
    if result.success():
        request.session["impersonated_user_uuid"] = str(user_uuid)
        # Explicitly save session to ensure it's committed before response is sent
        # This prevents race condition where page reloads before session is saved
        request.session.save()

    return result.json_response()


@extend_schema(
    summary="Stop impersonation",
    parameters=[],
    responses={
        200: {
            "type": "object",
            "properties": {
                "output": {
                    "type": "boolean",
                    "description": "True if impersonation stopped successfully",
                },
                "error": {"type": "boolean", "description": "False if successful"},
                "http_response_code": {
                    "type": "integer",
                    "description": "HTTP status code",
                },
                "error_messages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Error messages if any",
                },
            },
        },
        403: {
            "type": "object",
            "properties": {
                "output": {"type": "null"},
                "error": {"type": "boolean"},
                "http_response_code": {"type": "integer"},
                "error_messages": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    examples=[],
    description=(
        "Stop impersonating (admin/staff only). "
        "On success, the controller removes the impersonated user UUID from the session."
    ),
)
@api_view(["POST"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def stop_impersonation(request):
    """
    Stop impersonating a user.

    Only admin or staff users can stop impersonation.
    """
    # Call handler first to validate
    result = ImpersonationHandler.stop_impersonation(request.user)

    # Only remove from session if successful
    if result.success():
        request.session.pop("impersonated_user_uuid", None)
        # Explicitly save session to ensure it's committed before response is sent
        # This prevents race condition where page reloads before session is saved
        request.session.save()

    return result.json_response()


@extend_schema(
    summary="Get impersonation status",
    parameters=[],
    responses={
        200: {
            "type": "object",
            "properties": {
                "output": {
                    "type": "boolean",
                    "description": "True if currently impersonating, False otherwise",
                },
                "error": {"type": "boolean", "description": "False if successful"},
                "http_response_code": {
                    "type": "integer",
                    "description": "HTTP status code",
                },
                "error_messages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Error messages if any",
                },
            },
        },
        403: {
            "type": "object",
            "properties": {
                "output": {"type": "null"},
                "error": {"type": "boolean"},
                "http_response_code": {"type": "integer"},
                "error_messages": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    examples=[],
    description="Return a boolean indicating whether the current session is impersonating another user (admin/staff only).",
)
@api_view(["GET"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def impersonation_status(request):
    """
    Get current impersonation status.

    Returns whether the current session is impersonating another user.
    """
    impersonated_user = getattr(request, "impersonated_user", None)

    return ImpersonationHandler.get_impersonation_status(
        request.user, impersonated_user
    ).json_response()
