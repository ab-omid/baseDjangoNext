from app.utils.error_tracking import init_error_tracking
from .celery import celery as celery_app

init_error_tracking()

__all__ = "celery_app"
