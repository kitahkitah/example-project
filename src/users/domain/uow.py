from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing import Self

    from .repositories import UserRepository


class UserUnitOfWork(Protocol):
    """Unit of work for users."""

    user_repo: UserRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...  # type: ignore[no-untyped-def]  # noqa: ANN001

    def commit(self) -> None:
        """Commit changes."""
