from collections.abc import Iterable
from datetime import date

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from shared.errors import NotFoundError
from shared.infrastructure.sqlalchemy import Base

from ...domain.models import User, UserId
from ...errors import EmailIsUsedError


class UserSQLAlchemyModel(Base):
    """User model for SQLAlchemy ORM."""

    birth_date: Mapped[date]
    email: Mapped[str] = mapped_column(unique=True)
    email_confirmed: Mapped[bool]
    first_name: Mapped[str]
    id: Mapped[UserId] = mapped_column(primary_key=True, index=True)
    last_name: Mapped[str]

    __tablename__ = 'users'


class SQLAlchemyUserRepository:
    """A user repository based on SQLAlchemy.

    docs: https://www.sqlalchemy.org/
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def check_email_unique(self, email: str) -> None:
        """Check if email is unique.

        Raise:
            - EmailIsUsedError, if the email is already used;
        """
        if await self._session.scalar(exists().where(UserSQLAlchemyModel.email == email).select()):
            raise EmailIsUsedError

    async def create(self, user: User) -> None:
        """Create a new user."""
        db_user = UserSQLAlchemyModel(
            birth_date=user.birth_date,
            email=user.email,
            email_confirmed=user.email_confirmed,
            first_name=user.first_name,
            id=user.id,
            last_name=user.last_name,
        )
        self._session.add(db_user)

    async def get(self, id: UserId) -> User:
        """Obtain the user.

        Raise:
            - shared.errors.NotFoundError, if the user wasn't found
        """
        q = select(UserSQLAlchemyModel).where(UserSQLAlchemyModel.id == id)
        user = await self._session.scalar(q)

        if not user:
            raise NotFoundError

        return User(
            birth_date=user.birth_date,
            email=user.email,
            email_confirmed=user.email_confirmed,
            first_name=user.first_name,
            id=user.id,
            last_name=user.last_name,
        )

    async def list(self, ids: Iterable[UserId]) -> dict[UserId, User]:
        """Return users data."""
        q = select(UserSQLAlchemyModel).where(UserSQLAlchemyModel.id.in_(ids))
        users = await self._session.scalars(q)

        return {
            user.id: User(
                birth_date=user.birth_date,
                email=user.email,
                email_confirmed=user.email_confirmed,
                first_name=user.first_name,
                id=user.id,
                last_name=user.last_name,
            )
            for user in users
        }

    async def update(self, user: User) -> None:
        """Save the user changes."""
        updates = {k: getattr(user, k) for k in user.get_changed_fields()}
        q = update(UserSQLAlchemyModel).where(UserSQLAlchemyModel.id == user.id).values(**updates)
        await self._session.execute(q)

        user.clear_changed_fields()
