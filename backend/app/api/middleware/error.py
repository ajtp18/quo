from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class ErrorMiddleware(BaseHTTPMiddleware):
    """Error handling middleware"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        except Exception as exc:
            logger.error(f"Unexpected error: {exc}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            ) 