from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.schemas.user import User

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user = Depends(get_current_user)):
    """Get current user"""
    return current_user 