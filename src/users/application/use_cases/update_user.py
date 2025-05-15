from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Collection
    from datetime import date

    from ...domain.models import User, UserId
    from ...domain.uow import UserUnitOfWork


@dataclass(frozen=True, slots=True)
class UpdateUserDTO:
    """A DTO for a user update."""

    fields_to_update: Collection[str]

    birth_date: date | None = None
    email: str | None = None
    email_confirmed: bool | None = None
    first_name: str | None = None
    last_name: str | None = None


class UpdateUserUsecase:
    """A usecase for a user update."""

    def __init__(self, uow: UserUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: UserId, user_data: UpdateUserDTO) -> User:
        """Get the specified user. Update them."""
        async with self._uow:
            user = await self._uow.user_repo.get(user_id)

            for field in user_data.fields_to_update:
                setattr(user, field, getattr(user_data, field))

            await self._uow.user_repo.update(user)
            self._uow.commit()
        return user
