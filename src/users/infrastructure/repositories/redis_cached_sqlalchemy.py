from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, TypedDict
from uuid import UUID

import orjson

from ...domain.models import User, UserId
from .sqlalchemy import SQLAlchemyUserRepository

if TYPE_CHECKING:
    from collections.abc import Iterable

    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession


class UserRedisDict(TypedDict):
    """User model for Redis."""

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
            user_dict = orjson.loads(cached_data)
            user_dict['id'] = UserId(UUID(user_dict.pop('id')))
            user_dict['birth_date'] = date.fromisoformat(user_dict['birth_date'])
            return User(**user_dict)

        user = await super().get(id)

        user_dict = UserRedisDict(
            birth_date=user.birth_date,
            email=user.email,
            email_confirmed=user.email_confirmed,
            first_name=user.first_name,
            id=user.id,
            last_name=user.last_name,
        )
        await self._redis_con.set(key, orjson.dumps(user_dict), self.CACHE_TIMEOUT)
        return user

    async def list(self, ids: Iterable[UserId]) -> dict[UserId, User]:
        """Return users data."""
        users_data = {}

        non_cached_ids = []
        keys = [self.CACHE_KEY_PATTERN.format(user_id=id_) for id_ in ids]
        cached_data = await self._redis_con.mget(keys)
        for id_, user_data in zip(ids, cached_data, strict=False):
            if user_data:
                user_dict = orjson.loads(user_data)
                user_dict['id'] = UserId(UUID(user_dict['id']))
                user_dict['birth_date'] = date.fromisoformat(user_dict['birth_date'])
                users_data[id_] = User(**user_dict)
            else:
                non_cached_ids.append(id_)

        non_cached_users_data = await super().list(non_cached_ids)
        users_data.update(non_cached_users_data)

        async with self._redis_con.pipeline() as p:
            for user in non_cached_users_data.values():
                user_dict = UserRedisDict(
                    birth_date=user.birth_date,
                    email=user.email,
                    email_confirmed=user.email_confirmed,
                    first_name=user.first_name,
                    id=user.id,
                    last_name=user.last_name,
                )
                p.set(self.CACHE_KEY_PATTERN.format(user_id=user.id), orjson.dumps(user_dict), ex=self.CACHE_TIMEOUT)
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
