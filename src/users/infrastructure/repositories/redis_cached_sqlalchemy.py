from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from uuid import UUID

import orjson

from ...domain.models import User, UserId
from .sqlalchemy import SQLAlchemyUserRepository

if TYPE_CHECKING:
    from datetime import date

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
    """Derive from SQLAlchemyUserRepository user repository based on redis-om.

    docs: https://github.com/redis/redis-om-python
    """

    CACHE_KEY_PATTERN = 'users:{user_id}'

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
        await self._redis_con.set(key, orjson.dumps(user_dict))
        return user

    async def update(self, user: User) -> None:
        """Delete user cache. Save the user changes in super().

        Raise:
            - EmailIsUsedError, if the email is already used;
        """
        key = self.CACHE_KEY_PATTERN.format(user_id=user.id)
        await self._redis_con.delete(key)

        await super().update(user)
