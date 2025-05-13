from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, NewType

if TYPE_CHECKING:
    from collections.abc import Collection
    from datetime import date


@dataclass(frozen=True, slots=True)
class CreateUserParams:
    """Params for user creating."""

    birth_date: date
    email: str
    first_name: str
    last_name: str


@dataclass(frozen=True, slots=True)
class UpdateUserParams:
    """Params for user update."""

    fields_to_update: Collection[str]

    birth_date: date | None = None
    email: str | None = None
    email_confirmed: bool | None = None
    first_name: str | None = None
    last_name: str | None = None

    def __post_init__(self):
        if not self.fields_to_update:
            msg = 'fields_to_update is empty'
            raise ValueError(msg)


UpdateUserChanges = NewType('UpdateUserChanges', list[str])
