from datetime import UTC, date, datetime
from typing import Annotated, Self

from pydantic import BaseModel, EmailStr, Field, computed_field, model_validator

from ...domain.models import UserId


class ConfirmEmailRequest(BaseModel):
    """Create user request schema."""

    code: Annotated[str, Field(pattern=r'^\d{6}$')]


class CreateUserRequest(BaseModel):
    """Create user request schema."""

    birth_date: date
    email: EmailStr
    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]


class CreateUserResponse(BaseModel):
    """Create user response schema."""

    birth_date: date
    email: str
    email_confirmed: bool
    first_name: str
    id: UserId
    last_name: str


class GetOwnProfileResponse(BaseModel):
    """Get own profile response schema."""

    birth_date: date
    email: str
    email_confirmed: bool
    first_name: str
    id: UserId
    last_name: str


class GetUserResponse(BaseModel):
    """Get user response schema."""

    birth_date: Annotated[date, Field(exclude=True)]
    email_confirmed: bool
    first_name: str
    id: UserId

    @computed_field  # type: ignore[prop-decorator]
    @property
    def age(self) -> int:
        """Return age based on birth_date"""
        today = datetime.now(UTC).date()
        return (
            today.year
            - self.birth_date.year
            - int((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )


class UpdateUserRequest(BaseModel):
    """Create user request schema."""

    birth_date: date | None = None
    email: EmailStr | None = None
    first_name: Annotated[str, Field(min_length=1, max_length=50)] | None = None
    last_name: Annotated[str, Field(min_length=1, max_length=50)] | None = None

    @model_validator(mode='after')
    def require_one_field(self) -> Self:
        """Require at least one field."""
        if not any([self.birth_date, self.email, self.first_name, self.last_name]):
            msg = 'At least one field required'
            raise ValueError(msg)
        return self
