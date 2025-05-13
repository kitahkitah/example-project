from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class MailDTO:
    """A set of data used for mail sending."""

    content: str
    email_from: str
    email_to: str
    subject: str


class MailClient(Protocol):
    """A client for mail service."""

    async def send(self, mail: MailDTO) -> None:
        """Send an email."""
