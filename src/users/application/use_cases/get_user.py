from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.models import User, UserId
    from ...domain.uow import UserUnitOfWork


class GetUserUsecase:
    """A usecase for a user obtaining."""

    def __init__(self, uow: UserUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: UserId) -> User:
        """Get the specified user."""
        return await self._uow.user_repo.get(user_id)
