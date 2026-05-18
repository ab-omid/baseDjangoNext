from django.urls import path

from app.controllers.api_controller import (
    api_key_detail,
    api_key_generate,
    api_key_revoke,
    user_delete,
    user_detail,
    user_create,
    user_profile,
    user_profile_image_upload,
    user_profile_update,
    users_list,
    user_update,
)

urlpatterns = [
    path("", users_list, name="users_list"),
    path("create/", user_create, name="user_create"),
    path("profile/", user_profile, name="user_profile"),
    path("profile/update/", user_profile_update, name="user_profile_update"),
    path("profile/image/", user_profile_image_upload, name="user_profile_image_upload"),
    path("api-key/", api_key_detail, name="api_key_detail"),
    path("api-key/generate/", api_key_generate, name="api_key_generate"),
    path("api-key/revoke/", api_key_revoke, name="api_key_revoke"),
    path("<str:user_uuid>/", user_detail, name="user_detail"),
    path("<str:user_uuid>/update/", user_update, name="user_update"),
    path("<str:user_uuid>/delete/", user_delete, name="user_delete"),
]
