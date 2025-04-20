from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import Base
from app.db.session import engine

async def init_db() -> None:
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 