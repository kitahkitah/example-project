from __future__ import annotations

from typing import TYPE_CHECKING

from .repositories.redis_cached_sqlalchemy import RedisCachedSQLAlchemyUserRepository

if TYPE_CHECKING:
    from typing import Self

    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from ..domain.repositories import UserRepository


class UserSQLAlchemyUnitOfWork:
    """Unit of work for users."""

    def __init__(self, redis_connection: Redis, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._redis_con = redis_connection
        self._session_factory = session_factory
        self._to_commit = False

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self._session.begin()
        self.user_repo: UserRepository = RedisCachedSQLAlchemyUserRepository(self._redis_con, self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001
        try:
            if exc_type or not self._to_commit:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.aclose()

    def commit(self) -> None:
        """Commit changes."""
        self._to_commit = True
