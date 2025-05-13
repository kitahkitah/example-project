from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...domain.params_spec import UpdateUserParams
from .get_user import GetUserUsecase

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
        self._get_user_usecase = GetUserUsecase(uow)
        self._uow = uow

    async def execute(
        self, user_data: UpdateUserDTO, *, user: User | None = None, user_id: UserId | None = None
    ) -> User:
        """Get the specified user. Update them."""
        if not user:
            if user_id:
                user = await self._get_user_usecase.execute(user_id)
            else:
                msg = 'Either user or user_id must be set'
                raise ValueError(msg)

        params = UpdateUserParams(
            fields_to_update=user_data.fields_to_update,
            birth_date=user_data.birth_date,
            email=user_data.email,
            email_confirmed=user_data.email_confirmed,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        changed_fields = user.update(params)

        await self._uow.user_repo.update(user, changed_fields)
        self._uow.commit()
        return user
