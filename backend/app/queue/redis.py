from arq.connections import RedisSettings
from redis.asyncio import Redis

from app.core.config import settings


def get_arq_redis_settings() -> RedisSettings:
    redis = Redis.from_url(settings.redis_url)

    return RedisSettings(
        host=redis.connection_pool.connection_kwargs["host"],
        port=redis.connection_pool.connection_kwargs["port"],
        database=redis.connection_pool.connection_kwargs.get("db", 0),
        password=redis.connection_pool.connection_kwargs.get("password"),
    )   
