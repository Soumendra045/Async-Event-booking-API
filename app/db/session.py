from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker
)
from app.db.database import engine

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)
