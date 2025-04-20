from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.token_service import TokenService
from app.core.security import verify_token

security = HTTPBearer()
token_service = TokenService()

class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # routes that don't need authentication
        public_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            f"{settings.API_V1_STR}/openapi.json",
            f"{settings.API_V1_STR}/auth/login",
            f"{settings.API_V1_STR}/auth/register",
            f"{settings.API_V1_STR}/auth/refresh",
            f"{settings.API_V1_STR}/auth/logout",
            "/"
        ]
        
        if request.url.path in public_paths:
            return await call_next(request)

        try:
            credentials = await security(request)
            token = credentials.credentials
            
            is_blacklisted = await token_service.is_token_blacklisted(token)
            
            if is_blacklisted:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            payload = verify_token(token, token_type="access")
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token or wrong token type",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
        except HTTPException as e:
            raise e
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request) 