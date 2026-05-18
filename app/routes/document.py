"""
This module contains URL configuration for the Radar API documentation views.

The URL patterns are defined using Django's `path` function.

- `schema`: This view is responsible for generating the API schema using the Spectacular library.
- `swagger-ui`: This view provides a user-friendly interface for exploring and interacting with the API using Swagger.
- `redoc`: This view provides a more readable and searchable interface for exploring and interacting with the API using ReDoc.
"""

from django.urls import path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # URL pattern for generating the API schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # URL pattern for accessing the Swagger UI
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # URL pattern for accessing the ReDoc UI
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
