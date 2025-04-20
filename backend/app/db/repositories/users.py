from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.core.security import get_password_hash, verify_password

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email"""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, email: str, password: str, username: str | None = None) -> User:
        """Create new user"""
        db_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            username=username
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate user"""
        user = await self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_by_id(self, id: int) -> User | None:
        """Get user by ID"""
        result = await self.session.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none() 