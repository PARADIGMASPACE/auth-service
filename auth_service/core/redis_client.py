from redis.asyncio import Redis


class RedisClient:
    def __init__(self, host="redis", port=6379, db=0):
        self.redis = Redis(host=host, port=port, db=db)

    async def set_token(self, email, token, expire=3600):
        await self.redis.setex(email, expire, token)

    async def get_token(self, email):
        return await self.redis.get(email)

    async def delete_token(self, email):
        await self.redis.delete(email)

    async def close(self):
        await self.redis.aclose()

    async def key_exists(self, email):
        return await self.redis.exists(email) > 0


redisClient = RedisClient()