from app.config.base_config import BaseConfig


class AppConfig(BaseConfig):
    SECRET_KEY = BaseConfig.env(
        "APP_SECRET_KEY", default="django-insecure-*pq$9dsc5uoqf88wr52hep9#8^+20x)0ku(+s6w-5&0-1_&vbw"
    )
    DEBUG = BaseConfig.env.bool("APP_DEBUG", default=False)
    ALLOWED_HOSTS = BaseConfig.env.list("APP_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
    SETTINGS_MODULE = BaseConfig.env.str("APP_SETTINGS_MODULE", default="PDNR.settings")
    BASE_URL = BaseConfig.env.str("APP_BASE_URL", default='http://127.0.0.1:8000')
    FRONTEND_URL = BaseConfig.env.str("APP_FRONTEND_URL", default='http://127.0.0.1:5000')

    MEDIA_ROOT = BaseConfig.env.str("APP_MEDIA_ROOT", default='storage/media/')
    MEDIA_URL = BaseConfig.env.str("APP_MEDIA_URL", default='/storage/media/')
    STATIC_ROOT = BaseConfig.env.str("APP_STATIC_ROOT", default="storage/static/")
    STATIC_URL = BaseConfig.env.str("APP_STATIC_URL", default="/storage/static/")
    ERROR_TRACKING_DSN = BaseConfig.env.str("APP_ERROR_TRACKING_DSN", default="")
    ERROR_TRACKING_ENVIRONMENT = BaseConfig.env.str(
        "APP_ERROR_TRACKING_ENVIRONMENT", default="development"
    )
    ERROR_TRACKING_RELEASE = BaseConfig.env.str("APP_ERROR_TRACKING_RELEASE", default="")
    ERROR_TRACKING_TRACES_SAMPLE_RATE = BaseConfig.env.float(
        "APP_ERROR_TRACKING_TRACES_SAMPLE_RATE", default=0.0
    )
    ERROR_TRACKING_PROFILES_SAMPLE_RATE = BaseConfig.env.float(
        "APP_ERROR_TRACKING_PROFILES_SAMPLE_RATE", default=0.0
    )
    ERROR_TRACKING_SEND_PII = BaseConfig.env.bool("APP_ERROR_TRACKING_SEND_PII", default=False)
    ERROR_TRACKING_ENABLE_LOGS = BaseConfig.env.bool(
        "APP_ERROR_TRACKING_ENABLE_LOGS", default=False
    )
    ERROR_TRACKING_LOG_LEVEL = BaseConfig.env.str("APP_ERROR_TRACKING_LOG_LEVEL", default="ERROR")
