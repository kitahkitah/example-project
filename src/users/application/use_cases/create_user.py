from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...domain.models import User
from ...domain.params_spec import CreateUserParams

if TYPE_CHECKING:
    from datetime import date

    from ...domain.uow import UserUnitOfWork


@dataclass(frozen=True, slots=True)
class CreateUserDTO:
    """A DTO for a user creating."""

    birth_date: date
    email: str
    first_name: str
    last_name: str


class CreateUserUsecase:
    """A usecase for a user creating."""

    def __init__(self, uow: UserUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_data: CreateUserDTO) -> User:
        """Create a new user. Check email uniqueness."""
        params = CreateUserParams(
            birth_date=user_data.birth_date,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        user = User.create(params)

        async with self._uow:
            await self._uow.user_repo.check_email_unique(user.email)

            await self._uow.user_repo.create(user)
            self._uow.commit()
        return user
