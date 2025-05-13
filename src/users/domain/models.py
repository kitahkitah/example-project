from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, NewType
from uuid import UUID, uuid4

from ..errors import AgeRestrictionError
from .params_spec import UpdateUserChanges

if TYPE_CHECKING:
    from datetime import date
    from typing import Self

    from .params_spec import CreateUserParams, UpdateUserParams

UserId = NewType('UserId', UUID)


class User:
    """A user."""

    __slots__ = ('birth_date', 'email', 'email_confirmed', 'first_name', 'id', 'last_name')

    def __init__(  # noqa: PLR0913
        self, *, birth_date: date, email: str, email_confirmed: bool, first_name: str, id: UserId, last_name: str
    ) -> None:
        self.birth_date = birth_date
        self.email = email
        self.email_confirmed = email_confirmed
        self.first_name = first_name
        self.id = id
        self.last_name = last_name

    @classmethod
    def create(cls, params: CreateUserParams) -> Self:
        """Create a new user.

        Email of a new user is always NOT confirmed.
        """
        cls._validate(params.birth_date)

        email_confirmed = False
        id = UserId(uuid4())
        return cls(
            birth_date=params.birth_date,
            email=params.email,
            email_confirmed=email_confirmed,
            first_name=params.first_name,
            id=id,
            last_name=params.last_name,
        )

    def update(self, params: UpdateUserParams) -> UpdateUserChanges:
        """Update the user. Return a collection of changed fields.

        Changed email is always NOT confirmed.
        """
        if 'email_confirmed' in params.fields_to_update and 'email' in params.fields_to_update:
            msg = 'Impossible to change and confirm email at the same time'
            raise ValueError(msg)

        self._validate(params.birth_date)

        changes = UpdateUserChanges([])

        for field in params.fields_to_update:
            if field == 'email':
                self.email_confirmed = False
                changes.append('email_confirmed')

            setattr(self, field, getattr(params, field))
            changes.append(field)

        return changes

    @staticmethod
    def _validate(birth_date: date | None = None) -> None:
        """Validate:
        1) age >= 18, otherwise raise AgeRestrictionError;
        """
        if birth_date:
            today = datetime.now(UTC).date()
            if birth_date > today.replace(today.year - 18):
                raise AgeRestrictionError
