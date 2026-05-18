from app.config.base_config import BaseConfig


class CeleryConfig(BaseConfig):
    TASK_SERIALIZER: str = BaseConfig.env.str("CELERY_TASK_SERIALIZER", default="json")
    RESULT_SERIALIZER: str = BaseConfig.env.str("CELERY_RESULT_SERIALIZER", default="json")
    BROKER_URL: str = BaseConfig.env.str("CELERY_BROKER_URL", default="redis://REDIS:6379/0")
    RESULT_BACKEND: str = BaseConfig.env.str("CELERY_RESULT_BACKEND", default="redis://REDIS:6379/0")
