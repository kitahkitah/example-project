from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, TypedDict

from shared.infrastructure.redis import common as common_redis

from ...infrastructure.repositories.redis_cached_sqlalchemy import RedisCachedSQLAlchemyUserRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from ...domain.models import UserId


class UserDict(TypedDict):
    """User model for Redis."""

    age: int
    email_confirmed: bool
    first_name: str


async def get_users_data(ids: list[UserId], db_session: AsyncSession) -> dict[UserId, UserDict]:
    """Return users data by ids."""
    repo = RedisCachedSQLAlchemyUserRepository(common_redis, db_session)
    users_data = await repo.list(ids)

    users_dict = {}
    for user in users_data.values():
        today = datetime.now(UTC).date()
        age = (
            today.year
            - user.birth_date.year
            # - 1 year if the user's birthday has already passed
            - int((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
        )

        users_dict[user.id] = UserDict(age=age, email_confirmed=user.email_confirmed, first_name=user.first_name)

    return users_dict
