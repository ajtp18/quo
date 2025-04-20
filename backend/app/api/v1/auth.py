from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.deps import get_db
from app.db.repositories.users import UserRepository
from app.schemas.user import UserCreate, User, UserLogin
from app.schemas.token import Token, TokenPayload, RefreshTokenRequest, LogoutRequest
from app.core.security import create_token_pair, verify_token
from app.services.token_service import TokenService
from datetime import datetime
from jose import jwt, JWTError
from app.core.config import settings

router = APIRouter()
token_service = TokenService()

@router.post("/register", response_model=User)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register new user"""
    repo = UserRepository(db)
    user = await repo.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = await repo.create(email=user_in.email, password=user_in.password, username=user_in.username)
    return user

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user"""
    repo = UserRepository(db)
    user = await repo.authenticate(email=user_data.email, password=user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    access_token, refresh_token = create_token_pair(user.id)
    
    # Store refresh token
    await token_service.store_refresh_token(user.id, refresh_token)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """Get new access token using refresh token"""
    payload = verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if token is blacklisted
    if await token_service.is_token_blacklisted(request.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    # Create new token pair
    user_id = payload.get("sub")
    access_token, refresh_token = create_token_pair(user_id)
    
    # Update refresh token
    await token_service.store_refresh_token(user_id, refresh_token)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/logout")
async def logout(request: LogoutRequest):
    """Logout user and invalidate both tokens"""
    for token in [request.access_token, request.refresh_token]:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            user_id = payload.get("sub")
            expires = datetime.fromtimestamp(payload.get("exp"))
            
            await token_service.blacklist_token(token, expires)
            
            if payload.get("type") == "refresh":
                await token_service.remove_refresh_token(user_id)
                
        except JWTError:
            continue
    
    return {"message": "Successfully logged out"} 