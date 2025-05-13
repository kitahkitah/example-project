from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from ..application.protocols.mail_service import MailDTO


class FakeMailClient:
    """A fake client for mail service. Just prints mails."""

    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    async def send(self, mail: MailDTO) -> None:
        """Print a mail."""
        self._logger.info(mail.content)
        self._logger.info(mail.email_from)
        self._logger.info(mail.email_to)
        self._logger.info(mail.subject)
