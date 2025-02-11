from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@db:5432/moderation")

# Create async engine
engine = create_async_engine(DATABASE_URL, future=True, echo=True)

# Create async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
