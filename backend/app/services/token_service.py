from datetime import datetime, timedelta
from app.core.config import settings
from redis import asyncio as aioredis
import json

class TokenService:
    def __init__(self):
        self._redis = None

    async def _get_redis(self):
        if not self._redis:
            self._redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    async def store_refresh_token(self, user_id: int, refresh_token: str):
        """Store refresh token in Redis"""
        redis = await self._get_redis()
        key = f"{settings.REDIS_REFRESH_TOKEN_KEY_PREFIX}{user_id}"
        expiration = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
        await redis.set(
            key,
            refresh_token,
            ex=expiration
        )

    async def blacklist_token(self, token: str, expires_at: datetime):
        """Add token to blacklist"""
        redis = await self._get_redis()
        key = f"{settings.REDIS_BLACKLIST_KEY_PREFIX}{token}"
        
        now = datetime.utcnow()
        if expires_at <= now:
            expiration = settings.MIN_BLACKLIST_TIME
        else:
            expiration = max(
                int((expires_at - now).total_seconds()),
                settings.MIN_BLACKLIST_TIME
            )
        
        await redis.set(key, "1", ex=expiration)
        exists = await redis.exists(key)

    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        redis = await self._get_redis()
        key = f"{settings.REDIS_BLACKLIST_KEY_PREFIX}{token}"
        exists = await redis.exists(key)
        return exists

    async def get_refresh_token(self, user_id: int) -> str:
        """Get refresh token for user"""
        redis = await self._get_redis()
        key = f"{settings.REDIS_REFRESH_TOKEN_KEY_PREFIX}{user_id}"
        return await redis.get(key)

    async def remove_refresh_token(self, user_id: int):
        """Remove refresh token from Redis"""
        redis = await self._get_redis()
        key = f"{settings.REDIS_REFRESH_TOKEN_KEY_PREFIX}{user_id}"
        await redis.delete(key)

    async def cleanup_blacklist(self):
        """Remove expired tokens from blacklist"""
        redis = await self._get_redis()

        pass 