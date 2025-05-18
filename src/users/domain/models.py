from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, NewType
from uuid import UUID, uuid4

from shared.domain.models import Entity

from ..errors import AgeRestrictionError

if TYPE_CHECKING:
    from datetime import date
    from typing import Self

    from .params_spec import CreateUserParams

UserId = NewType('UserId', UUID)


class User(Entity):
    """A user.

    Fields 'first_name' and 'last_name' are important for domain logic.
    Their use can be implemented later for passports verification.
    """

    __slots__ = ('_birth_date', '_email', '_id', 'email_confirmed', 'first_name', 'last_name')

    def __init__(
        self,
        *,
        birth_date: date,
        email: str,
        email_confirmed: bool,
        first_name: str,
        id: UserId,
        last_name: str,
        _for_creating: bool = False,
    ) -> None:
        self.email_confirmed = email_confirmed
        self.first_name = first_name
        self._id = id
        self.last_name = last_name

        if not _for_creating:  # i.e. just initializing, validation not required
            self._birth_date = birth_date
            self._email = email
        else:
            self.birth_date = birth_date
            self._email = ''
            self.email = email

        super().__init__()

    @classmethod
    def create(cls, params: CreateUserParams) -> Self:
        """Create a new user.

        Email of a new user is always NOT confirmed.
        """
        email_confirmed = False
        id = UserId(uuid4())

        return cls(
            birth_date=params.birth_date,
            email=params.email,
            email_confirmed=email_confirmed,
            first_name=params.first_name,
            id=id,
            last_name=params.last_name,
            _for_creating=True,
        )

    @property
    def birth_date(self) -> date:
        """Return birth_date."""
        return self._birth_date

    @birth_date.setter
    def birth_date(self, value: date) -> None:
        """Validate age >= 18 or raise AgeRestrictionError."""
        today = datetime.now(UTC).date()
        if value > today.replace(today.year - 18):
            raise AgeRestrictionError

        self._birth_date = value

    @property
    def email(self) -> str:
        """Return email."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Set a new email. Changed email is always NOT confirmed."""
        if self.email == value:
            return

        self._email = value
        self.email_confirmed = False

    @property
    def id(self) -> UserId:
        """Return id."""
        return self._id
