from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ...domain.models import UserId

EMAIL_CONFIRMATION_CODE_TIMEOUT_SECS = 15 * 60  # 15 mins


class EmailConfirmationCodeServiceValidationError(Exception):
    """Code validation error."""


class EmailConfirmationCodeService(Protocol):
    """Email confirmation code service. Generates and verifies codes."""

    async def generate(self, user_id: UserId, email: str) -> str:
        """Generate a code that is valid for EMAIL_CONFIRMATION_CODE_TIMEOUT_SECS."""

    async def verify(self, user_id: UserId, email: str, code: str) -> None:
        """Verify the code.

        Raise:
            - EmailConfirmationCodeServiceValidationError, if the code isn't valid;
        """
