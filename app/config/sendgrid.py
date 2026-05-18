from app.config.base_config import BaseConfig


class SendGridConfig(BaseConfig):
    API_KEY: str = BaseConfig.env.str("SENDGRID_API_KEY", default="NONE")
    DEFAULT_FROM_EMAIL: str = BaseConfig.env.str("SENDGRID_DEFAULT_FROM_EMAIL", default="noreply@pdnr.com")
    DEFAULT_FROM_NAME: str = BaseConfig.env.str("SENDGRID_DEFAULT_FROM_NAME", default="pdnr")
