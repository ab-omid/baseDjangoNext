"""
This module contains custom rate throttling classes for the app API.

- `AnonRateThrottle`: Throttle class for anonymous users.
- `UserRateThrottle`: Throttle class for authenticated users.
- `AdminRateThrottle`: Throttle class for administrators.
- `PipelineRateThrottle`: Throttle class for pipeline operations.

Each throttle class inherits from `AnonRateThrottle`, `UserRateThrottle`, or `AdminRateThrottle` and overrides the `get_rate` method to specify the rate limit.

The rate limits are configured in the `ThrottlingConfig` class from the `app.config.throttling` module.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from app.config.throttling import ThrottlingConfig


class AnonRateThrottle(AnonRateThrottle):
    """
    Throttle class for anonymous users.

    The rate limit is obtained from the `ThrottlingConfig` class.
    """

    def get_rate(self):
        return ThrottlingConfig.ANON_RATE if ThrottlingConfig.ENABLED else None


class UserRateThrottle(UserRateThrottle):
    """
    Throttle class for authenticated users.

    The rate limit is obtained from the `ThrottlingConfig` class.
    """

    def get_rate(self):
        return ThrottlingConfig.USER_RATE if ThrottlingConfig.ENABLED else None


class AdminRateThrottle(UserRateThrottle):
    """
    Throttle class for administrators.

    The rate limit is obtained from the `ThrottlingConfig` class.
    """

    def get_rate(self):
        return ThrottlingConfig.ADMIN_RATE if ThrottlingConfig.ENABLED else None


class PipelineRateThrottle(AdminRateThrottle):
    """
    Throttle class for pipeline operations.

    The rate limit is obtained from the `ThrottlingConfig` class.
    """

    def get_rate(self):
        return ThrottlingConfig.PIPELINE_RATE if ThrottlingConfig.ENABLED else None
