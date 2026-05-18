from app.config.base_config import BaseConfig


class UnipileConfig(BaseConfig):
    INCOMING_REQUESTS_API_KEY: str = BaseConfig.env.str("UNIPILE_INCOMING_REQUESTS_API_KEY", default="None")
    API_KEY: str = BaseConfig.env.str("UNIPILE_API_KEY", default="None")
    BASE_URL: str = BaseConfig.env.str("UNIPILE_BASE_URL", default="https://api1.unipile.com:13111/api/v1/")
