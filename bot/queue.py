import os

from arq import ArqRedis, create_pool
from arq.connections import RedisSettings


def get_redis_settings() -> RedisSettings:
    return RedisSettings.from_dsn(os.environ.get("REDIS_URL", "redis://redis:6379"))


async def create_queue_pool() -> ArqRedis:
    return await create_pool(get_redis_settings())
