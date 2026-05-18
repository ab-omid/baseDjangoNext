from django.core.cache import cache
import redis


class CacheUtil:
    @staticmethod
    def get_client():
        from app.config.redis import RedisConfig

        return redis.Redis(
            host=RedisConfig.HOST, port=RedisConfig.PORT, db=RedisConfig.DB, password=RedisConfig.PASSWORD
        )

    @staticmethod
    def set(key, value, ttl = None):
        cache.set(key, value, ttl)

    @staticmethod
    def get(key):
        return cache.get(key)
