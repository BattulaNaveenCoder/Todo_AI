"""Async database session configuration and dependency injection."""

import logging
import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    logger.warning("DATABASE_URL is not set — database operations will fail")

# Async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL logging for development — disable in production
    pool_size=5,
    max_overflow=10,
)

# Session factory bound to the async engine
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session.

    Yields an AsyncSession and ensures cleanup on completion.
    The session acts as the unit-of-work boundary — commit in the
    Service layer, rollback is automatic on exception.
    """
    session = async_session()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
