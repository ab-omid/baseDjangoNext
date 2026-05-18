from app.config.base_config import BaseConfig


class ThrottlingConfig(BaseConfig):
    ENABLED: bool = BaseConfig.env.bool("THROTTLING_ENABLED", default=True)
    USER_RATE: str = BaseConfig.env.str("THROTTLING_USER_RATE", default="1000/minute")
    ANON_RATE: str = BaseConfig.env.str("THROTTLING_ANON_RATE", default="100/minute")
    ADMIN_RATE: str = BaseConfig.env.str("THROTTLING_ADMIN_RATE", default=None)
    PIPELINE_RATE: str = BaseConfig.env.str("THROTTLING_PIPELINE_RATE", default=None)
