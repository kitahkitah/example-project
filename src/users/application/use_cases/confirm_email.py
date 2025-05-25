from __future__ import annotations

from typing import TYPE_CHECKING

from ...errors import EmailConfirmationCodeError, EmailIsConfirmedError
from ..protocols.email_confirmation_code_service import (
    EmailConfirmationCodeService,
    EmailConfirmationCodeServiceValidationError,
)

if TYPE_CHECKING:
    from ...domain.models import UserId
    from ...domain.uow import UserUnitOfWork


class ConfirmEmailUsecase:
    """A usecase for an email confirmation."""

    def __init__(self, uow: UserUnitOfWork, email_confirmation_code_service: EmailConfirmationCodeService) -> None:
        self._email_confirmation_code_service = email_confirmation_code_service
        self._uow = uow

    async def execute(self, user_id: UserId, code: str) -> None:
        """Get the user. Verify confirmation string. Update the user.

        Raise:
            - EmailIsConfirmedError, if user's email is already confirmed;
            - EmailConfirmationCodeError, if the code is invalid;
        """
        async with self._uow:
            user = await self._uow.user_repo.get(user_id)
            if user.email_confirmed:
                raise EmailIsConfirmedError

            try:
                await self._email_confirmation_code_service.verify(user_id, user.email, code)
            except EmailConfirmationCodeServiceValidationError:
                raise EmailConfirmationCodeError from None

            user.email_confirmed = True

            await self._uow.user_repo.update(user)
            self._uow.commit()
