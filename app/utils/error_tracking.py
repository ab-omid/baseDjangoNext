"""
Error tracking initialization utilities.

Where: process startup for Django web and Celery worker/beat.
Uses: AppConfig environment settings and sentry-sdk integrations.
Behavior: initializes SDK once; no-op when DSN is not configured.
"""

from __future__ import annotations

import logging

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.config.app import AppConfig

_initialized = False


def _resolve_log_level(level_name: str) -> int:
    """Convert log-level text to logging level with a safe fallback."""
    level = getattr(logging, level_name.upper(), None)
    if isinstance(level, int):
        return level
    return logging.ERROR


def init_error_tracking() -> None:
    """Initialize error tracking for Django and Celery.

    The function intentionally does nothing when the DSN is missing so local/dev
    environments do not need any additional setup.
    """

    global _initialized
    if _initialized:
        return

    dsn = AppConfig.ERROR_TRACKING_DSN
    if not dsn:
        return

    log_level = _resolve_log_level(AppConfig.ERROR_TRACKING_LOG_LEVEL)
    logging_integration = LoggingIntegration(
        level=logging.INFO,
        event_level=log_level if AppConfig.ERROR_TRACKING_ENABLE_LOGS else None,
    )

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            logging_integration,
        ],
        environment=AppConfig.ERROR_TRACKING_ENVIRONMENT,
        release=AppConfig.ERROR_TRACKING_RELEASE or None,
        traces_sample_rate=AppConfig.ERROR_TRACKING_TRACES_SAMPLE_RATE,
        profiles_sample_rate=AppConfig.ERROR_TRACKING_PROFILES_SAMPLE_RATE,
        send_default_pii=AppConfig.ERROR_TRACKING_SEND_PII,
    )
    _initialized = True
