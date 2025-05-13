from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from shared.errors import NotFoundError as NotFoundError

if TYPE_CHECKING:
    from .models import User, UserId
    from .params_spec import UpdateUserChanges


class UserRepository(Protocol):
    """A user repository."""

    async def create(self, user: User) -> None:
        """Create a new user.

        Raise:
            - EmailIsUsedError, if the email is already used;
        """

    async def get(self, id: UserId) -> User:
        """Obtain the user.

        Raise:
            - shared.errors.NotFoundError, if the user wasn't found;
        """

    async def update(self, user: User, to_update: UpdateUserChanges) -> None:
        """Save the user changes.

        Raise:
            - EmailIsUsedError, if the email is already used;
        """
