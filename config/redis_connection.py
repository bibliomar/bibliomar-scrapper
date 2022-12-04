import aioredis
from aioredis import RedisError, Redis
from aioredis.exceptions import ConnectionError
from keys import redis_provider


class RedisConnection:
    def __init__(self):
        self.redis: Redis = aioredis.from_url(redis_provider)

    async def _is_redis_alive(self):
        try:
            await self.redis.ping()
            return True
        except RedisError as e:
            print(e)
            return False

    async def __aenter__(self) -> Redis:
        test = await self._is_redis_alive()
        if not test:
            raise ConnectionError("Could not connect to Redis.")

        return self.redis

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if await self._is_redis_alive():
            await self.redis.close()

        return True
