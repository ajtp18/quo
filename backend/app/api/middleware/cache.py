from fastapi import Request
from redis import asyncio as aioredis
from app.core.config import settings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse, StreamingResponse
import json

class CacheMiddleware(BaseHTTPMiddleware):
    """Cache middleware for GET requests"""
    
    def __init__(self, app):
        super().__init__(app)
        self.redis = None

    async def init_redis(self):
        """Initialize Redis connection"""
        try:
            if not self.redis:
                self.redis = await aioredis.from_url(
                    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                    password=settings.REDIS_PASSWORD or None,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.redis.ping()
        except Exception:
            self.redis = None

    async def get_cache(self, key: str) -> str | None:
        """Get value from cache"""
        await self.init_redis()
        return await self.redis.get(key)

    async def set_cache(self, key: str, value: str, expire: int = 300):
        """Set value in cache"""
        await self.init_redis()
        await self.redis.set(key, value, ex=expire)

    async def dispatch(self, request: Request, call_next):
        if request.method != "GET":
            return await call_next(request)

        skip_cache_paths = ["/docs", "/redoc", "/openapi.json", f"{settings.API_V1_STR}/auth"]
        if any(request.url.path.startswith(path) for path in skip_cache_paths):
            return await call_next(request)

        cache_key = f"cache:{request.url.path}"
        cached_response = await self.get_cache(cache_key)
        
        if cached_response:
            return JSONResponse(content=json.loads(cached_response))
        
        response = await call_next(request)
        
        if response.status_code == 200:
            try:
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                
                content = json.loads(response_body.decode())
                await self.set_cache(cache_key, json.dumps(content))
                return JSONResponse(content=content)
                
            except Exception:
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        
        return response 