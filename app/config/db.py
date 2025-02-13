from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, session
from sqlalchemy import create_engine
import os

# Async Configuration (for FastAPI)
DATABASE_URL_ASYNC = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@db:5432/moderation")
async_engine = create_async_engine(DATABASE_URL_ASYNC, future=True, echo=True)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

# Sync Configuration (for Celery)
DATABASE_URL_SYNC = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/moderation").replace("+asyncpg", "")
sync_engine = create_engine(DATABASE_URL_SYNC)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

# Dependency for FastAPI async sessions
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session