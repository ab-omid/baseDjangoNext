from app.config.base_config import BaseConfig


class DatabaseConfig(BaseConfig):
    ENGINE = BaseConfig.env.str("DB_ENGINE", default="django.db.backends.postgresql_psycopg2")
    NAME = BaseConfig.env.str("DB_NAME", default="pdnr")
    USER = BaseConfig.env("DB_USER", default="postgres")
    PASSWORD = BaseConfig.env("DB_PASSWORD", default="secret")
    HOST = BaseConfig.env("DB_HOST", default="localhost")
    PORT = BaseConfig.env("DB_PORT", default="5432")
