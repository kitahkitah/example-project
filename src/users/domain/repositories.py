from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from shared.errors import NotFoundError as NotFoundError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .models import User, UserId


class UserRepository(Protocol):
    """A user repository."""

    async def check_email_unique(self, email: str) -> None:
        """Check if email is unique.

        Raise:
            - EmailIsUsedError, if the email is already used;
        """

    async def create(self, user: User) -> None:
        """Create a new user."""

    async def get(self, id: UserId) -> User:
        """Obtain the user.

        Raise:
            - shared.errors.NotFoundError, if the user wasn't found;
        """

    async def list(self, ids: Iterable[UserId]) -> dict[UserId, User]:
        """Return users data."""

    async def update(self, user: User) -> None:
        """Save the user changes."""
