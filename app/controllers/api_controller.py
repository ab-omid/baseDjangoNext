from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema
from django.utils.dateparse import parse_datetime

from app.actions.action import Action
from app.handlers.api_handler import ApiHandler
from app.utils.throttling import AnonRateThrottle, UserRateThrottle
from app.models.user import User
from app.models.job import Job


@extend_schema(
    summary="List users",
    parameters=[
        OpenApiParameter(
            name="search",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Search term for filtering users",
        ),
        OpenApiParameter(
            name="page_token",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Pagination token",
        ),
        OpenApiParameter(
            name="max_results",
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Maximum number of users to return (default: 10)",
        ),
    ],
    responses={200: Action.generate_schema(User.api_response_schema())},
    examples=[],
    description="returns a list of users",
)
@api_view(["GET"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def users_list(request):
    current_user = getattr(request, "impersonated_user", None) or request.user
    search = request.GET.get("search")
    page_token = request.GET.get("page_token")
    max_results = request.GET.get("max_results")

    # Convert max_results to int if provided, otherwise use default
    if max_results is not None:
        try:
            max_results = int(max_results)
        except ValueError:
            max_results = 10
    else:
        max_results = 10

    return ApiHandler.users(
        current_user, search, page_token, max_results
    ).json_response()

@extend_schema(
    summary="Create user",
    parameters=[],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "User name"},
                "email": {"type": "string", "description": "User email"},
                "password": {"type": "string", "description": "Initial user password"},
                "status": {
                    "type": "string",
                    "enum": ["ACTIVE", "SUSPENDED", "DELETED"],
                    "description": "User status",
                },
                "is_staff": {"type": "boolean", "description": "Staff status"},
                "is_superuser": {"type": "boolean", "description": "Superuser status"},
            },
            "required": ["name", "email", "password"],
        }
    },
    responses={200: Action.generate_schema(User.api_response_schema())},
    examples=[],
    description="Create a new user (admin/staff only)",
)
@api_view(["POST"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def user_create(request):
    current_user = getattr(request, "impersonated_user", None) or request.user
    name = request.data.get("name")
    email = request.data.get("email")
    password = request.data.get("password")
    status = request.data.get("status")
    is_staff = request.data.get("is_staff")
    is_superuser = request.data.get("is_superuser")

    return ApiHandler.create_user(
        current_user=current_user,
        name=name,
        email=email,
        password=password,
        status=status,
        is_staff=is_staff,
        is_superuser=is_superuser,
    ).json_response()


@extend_schema(
    summary="Get user details",
    parameters=[
        OpenApiParameter(
            name="user_uuid",
            type=str,
            location=OpenApiParameter.PATH,
            required=True,
            description="User UUID",
        ),
        OpenApiParameter(
            name="add_statistics",
            type=bool,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Include statistics in response",
        ),
    ],
    responses={200: Action.generate_schema(User.api_response_schema())},
    examples=[],
    description="Get user details by UUID",
)
@api_view(["GET"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def user_detail(request, user_uuid):
    current_user = getattr(request, "impersonated_user", None) or request.user
    return ApiHandler.user_detail(
        current_user, user_uuid
    ).json_response()


@extend_schema(
    summary="Update user",
    parameters=[
        OpenApiParameter(
            name="user_uuid",
            type=str,
            location=OpenApiParameter.PATH,
            required=True,
            description="User UUID",
        )
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "User name"},
                "email": {"type": "string", "description": "User email"},
                "status": {
                    "type": "string",
                    "enum": ["ACTIVE", "SUSPENDED", "DELETED"],
                    "description": "User status",
                },
                "is_staff": {"type": "boolean", "description": "Staff status"},
                "is_superuser": {"type": "boolean", "description": "Superuser status"},
            },
        }
    },
    responses={200: Action.generate_schema(User.api_response_schema())},
    examples=[],
    description="Update user by UUID",
)
@api_view(["PATCH"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def user_update(request, user_uuid):
    current_user = getattr(request, "impersonated_user", None) or request.user
    name = request.data.get("name")
    email = request.data.get("email")
    status = request.data.get("status")
    is_staff = request.data.get("is_staff")
    is_superuser = request.data.get("is_superuser")

    return ApiHandler.update_user(
        current_user=current_user,
        target_user_uuid=user_uuid,
        name=name,
        email=email,
        status=status,
        is_staff=is_staff,
        is_superuser=is_superuser,
    ).json_response()


@extend_schema(
    summary="Delete user",
    parameters=[
        OpenApiParameter(
            name="user_uuid",
            type=str,
            location=OpenApiParameter.PATH,
            required=True,
            description="User UUID",
        )
    ],
    responses={
        204: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Success message"}
            },
        }
    },
    examples=[],
    description="Delete user by UUID",
)
@api_view(["DELETE"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def user_delete(request, user_uuid):
    current_user = getattr(request, "impersonated_user", None) or request.user
    return ApiHandler.delete_user(current_user, user_uuid).json_response()


@api_view(["GET"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def user_profile(request):
    current_user = getattr(request, "impersonated_user", None) or request.user
    return ApiHandler.user_profile(
        current_user
    ).json_response()


@extend_schema(
    summary="Update user profile",
    parameters=[],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "User name"},
                "email": {"type": "string", "description": "User email"},
                "password": {
                    "type": "string",
                    "description": "New password (optional)",
                }
            },
        }
    },
    responses={200: Action.generate_schema(User.api_response_schema())},
    examples=[],
    description="Update current user profile",
)
@api_view(["PATCH"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def user_profile_update(request):
    current_user = getattr(request, "impersonated_user", None) or request.user
    name = request.data.get("name")
    email = request.data.get("email")
    password = request.data.get("password")

    return ApiHandler.update_user_profile(
        current_user, name, email, password
    ).json_response()


@extend_schema(
    summary="Create user profile image upload",
    parameters=[],
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "profile_image": {
                    "type": "string",
                    "format": "binary",
                    "description": "Profile image file",
                }
            },
        }
    },
    responses={200: Action.generate_schema(User.api_response_schema())},
    examples=[],
    description="Upload profile image",
)
@api_view(["POST"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def user_profile_image_upload(request):
    current_user = getattr(request, "impersonated_user", None) or request.user
    profile_image = request.FILES.get("profile_image")

    if not profile_image:
        return ApiHandler.bad_request(["Profile image file is required"])

    return ApiHandler.upload_user_profile_image(
        current_user, profile_image
    ).json_response()

# ── API Key Management ────────────────────────────────────────────────────


@extend_schema(
    summary="Get API key details",
    parameters=[],
    responses={200: Action.generate_schema({"type": "object"}, is_single_output=True)},
    examples=[],
    description="Get the current user's API key metadata (prefix, scopes, last_used_at). Never returns the raw key.",
)
@api_view(["GET"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def api_key_detail(request):
    current_user = getattr(request, "impersonated_user", None) or request.user
    return ApiHandler.get_api_key(current_user).json_response()


@extend_schema(
    summary="Generate API key",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Human-readable label for the key (default: 'Default')",
                },
                "scopes": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["READ", "WRITE"]},
                    "description": "Permission scopes (default: ['READ', 'WRITE'])",
                },
            },
        }
    },
    responses={200: Action.generate_schema({"type": "object"}, is_single_output=True)},
    examples=[],
    description="Generate a new API key. Revokes any existing key. The raw key is returned only once.",
)
@api_view(["POST"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def api_key_generate(request):
    current_user = getattr(request, "impersonated_user", None) or request.user
    name = request.data.get("name")
    scopes = request.data.get("scopes")
    return ApiHandler.generate_api_key(
        user=current_user,
        name=name,
        scopes=scopes,
    ).json_response()


@extend_schema(
    summary="Revoke API key",
    parameters=[],
    responses={200: Action.generate_schema({"type": "object"}, is_single_output=True)},
    examples=[],
    description="Revoke the current user's API key.",
)
@api_view(["DELETE"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@permission_classes([IsAuthenticated])
def api_key_revoke(request):
    current_user = getattr(request, "impersonated_user", None) or request.user
    return ApiHandler.revoke_api_key(current_user).json_response()