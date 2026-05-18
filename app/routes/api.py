"""Main API route registry."""

from django.urls import include, path

urlpatterns = [
    path("", include("app.routes.auth")),
    path("", include("app.routes.impersonation")),
    path("user/", include("app.routes.user"))
]
