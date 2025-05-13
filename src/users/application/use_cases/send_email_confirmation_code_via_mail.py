from __future__ import annotations

from typing import TYPE_CHECKING

from ..protocols.email_confirmation_code_service import EMAIL_CONFIRMATION_CODE_TIMEOUT_SECS
from ..protocols.mail_service import MailDTO
from .get_user import GetUserUsecase

if TYPE_CHECKING:
    from ...domain.models import UserId
    from ...domain.uow import UserUnitOfWork
    from ..protocols.email_confirmation_code_service import EmailConfirmationCodeService
    from ..protocols.mail_service import MailClient


class SendEmailConfirmationCodeUsecase:
    """Email confirmation usecase that generates a confirmation code and sends it."""

    def __init__(
        self,
        uow: UserUnitOfWork,
        email_confirmation_code_service: EmailConfirmationCodeService,
        mail_client: MailClient,
        email_from: str,
    ) -> None:
        self._email_confirmation_code_service = email_confirmation_code_service
        self._email_from = email_from
        self._get_user_usecase = GetUserUsecase(uow)
        self._mail_client = mail_client

    async def execute(self, user_id: UserId) -> None:
        """Get the user, generate a confirmation code, send it."""
        user = await self._get_user_usecase.execute(user_id)

        code = await self._email_confirmation_code_service.generate(user_id, user.email)

        # You can always make it a Jinja template
        html_content = (
            '<!DOCTYPE html><head><meta charset="UTF-8"><title>Email confirmation</title></head>'
            f'<body><p>Your code: {code}.<br>'
            f'The code is valid for {EMAIL_CONFIRMATION_CODE_TIMEOUT_SECS / 60:.0f} minutes.</p></body></html>'
        )
        mail = MailDTO(
            content=html_content, email_from=self._email_from, email_to=user.email, subject='Email confirmation'
        )
        await self._mail_client.send(mail)
