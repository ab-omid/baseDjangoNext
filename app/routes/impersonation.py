"""Impersonation API routes."""

from django.urls import path

from app.controllers.impersonation_controller import (
    impersonation_status,
    start_impersonation,
    stop_impersonation,
)

urlpatterns = [
    path("impersonation/start/", start_impersonation, name="start_impersonation"),
    path("impersonation/stop/", stop_impersonation, name="stop_impersonation"),
    path("impersonation/status/", impersonation_status, name="impersonation_status"),
]
