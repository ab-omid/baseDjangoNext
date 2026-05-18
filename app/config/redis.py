from app.config.base_config import BaseConfig


class RedisConfig(BaseConfig):
    HOST = BaseConfig.env.str("REDIS_HOST", default="redis")
    PORT = BaseConfig.env.int("REDIS_PORT", default=6379)
    DB = BaseConfig.env.int("REDIS_DB", default=0)
    PASSWORD = BaseConfig.env.str("REDIS_PASSWORD", default="")
    KEY_PREFIX = BaseConfig.env.str("REDIS_KEY_PREFIX", default="pdnr:")
    URL = f"redis://:{PASSWORD}@{HOST}:{PORT}/{DB}"
