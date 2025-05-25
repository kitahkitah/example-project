from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from ...domain.models import User, UserId
from .sqlalchemy import SQLAlchemyUserRepository

if TYPE_CHECKING:
    from collections.abc import Iterable

    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession


class UserRedisModel(BaseModel):
    """User model for Redis."""

    model_config = ConfigDict(from_attributes=True)

    birth_date: date
    email: str
    email_confirmed: bool
    first_name: str
    id: UserId
    last_name: str


class RedisCachedSQLAlchemyUserRepository(SQLAlchemyUserRepository):
    """Derive from SQLAlchemyUserRepository user repository based on redis cache.

    docs: https://github.com/redis/redis-py
    """

    CACHE_KEY_PATTERN = 'users:{user_id}'
    CACHE_TIMEOUT = 60 * 60 * 24  # 1 day

    def __init__(self, redis_connection: Redis, session: AsyncSession) -> None:
        self._redis_con = redis_connection

        super().__init__(session)

    async def get(self, id: UserId) -> User:
        """Obtain the cached user. If not found, call super(), then cache it.

        Raise:
            - shared.errors.NotFoundError, if the user wasn't found at all
        """
        key = self.CACHE_KEY_PATTERN.format(user_id=id)
        if cached_data := await self._redis_con.get(key):
            redis_user = UserRedisModel.model_validate_json(cached_data)
            return User(**redis_user.model_dump())

        user = await super().get(id)

        redis_user = UserRedisModel.model_validate(user)
        await self._redis_con.set(key, redis_user.model_dump_json(), self.CACHE_TIMEOUT)
        return user

    async def list(self, ids: Iterable[UserId]) -> dict[UserId, User]:
        """Return users data."""
        users_data = {}

        # Tries to get all users from cache
        non_cached_ids = []
        keys = [self.CACHE_KEY_PATTERN.format(user_id=id_) for id_ in ids]
        cached_data = await self._redis_con.mget(keys)
        for id_, user_data in zip(ids, cached_data, strict=False):
            if user_data:
                redis_user = UserRedisModel.model_validate_json(user_data)
                users_data[id_] = User(**redis_user.model_dump())
            else:
                non_cached_ids.append(id_)

        # Obtains non cached users from db and then caches them
        non_cached_users_data = await super().list(non_cached_ids)
        users_data.update(non_cached_users_data)

        async with self._redis_con.pipeline() as p:
            for user in non_cached_users_data.values():
                redis_user = UserRedisModel.model_validate(user)

                key = self.CACHE_KEY_PATTERN.format(user_id=user.id)
                p.set(key, redis_user.model_dump_json(), ex=self.CACHE_TIMEOUT)
            await p.execute()

        return users_data

    async def update(self, user: User) -> None:
        """Delete user cache. Save the user changes in super().

        Raise:
            - EmailIsUsedError, if the email is already used;
        """
        key = self.CACHE_KEY_PATTERN.format(user_id=user.id)
        await self._redis_con.delete(key)

        await super().update(user)
