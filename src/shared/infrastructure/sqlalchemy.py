from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

if settings.DEBUG:
    engine = create_async_engine(
        settings.DATABASE_URL, pool_size=3, max_overflow=1, pool_recycle=1800, echo=settings.DEBUG
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL, pool_size=10, max_overflow=5, pool_recycle=1800, echo=settings.DEBUG
    )

sessionmaker = async_sessionmaker(autoflush=False, expire_on_commit=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all models."""
