from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date


@dataclass(frozen=True, slots=True)
class CreateUserParams:
    """Params for user creating."""

    birth_date: date
    email: str
    first_name: str
    last_name: str
