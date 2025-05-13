from __future__ import annotations

from typing import TYPE_CHECKING

from ...errors import EmailConfirmationCodeError
from ..protocols.email_confirmation_code_service import (
    EmailConfirmationCodeService,
    EmailConfirmationCodeServiceValidationError,
)
from .get_user import GetUserUsecase
from .update_user import UpdateUserDTO, UpdateUserUsecase

if TYPE_CHECKING:
    from ...domain.models import UserId
    from ...domain.uow import UserUnitOfWork


class ConfirmEmailUsecase:
    """A usecase for an email confirmation."""

    def __init__(self, uow: UserUnitOfWork, email_confirmation_code_service: EmailConfirmationCodeService) -> None:
        self._email_confirmation_code_service = email_confirmation_code_service
        self._get_user_usecase = GetUserUsecase(uow)
        self._update_user_usecase = UpdateUserUsecase(uow)

    async def execute(self, user_id: UserId, code: str) -> None:
        """Get the user. Verify confirmation string. Update the user."""
        user = await self._get_user_usecase.execute(user_id)

        try:
            await self._email_confirmation_code_service.verify(user_id, user.email, code)
        except EmailConfirmationCodeServiceValidationError:
            raise EmailConfirmationCodeError from None

        update_dto = UpdateUserDTO(email_confirmed=True, fields_to_update=('email_confirmed',))
        await self._update_user_usecase.execute(update_dto, user=user)
