from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost/postgres"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass