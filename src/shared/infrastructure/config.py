from functools import cached_property

from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Envs."""

    CORS_ORIGINS_REGEX: str
    DEBUG: bool = False
    EMAIL_FROM: str
    POSTGRESQL_HOST: str
    POSTGRESQL_NAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_PORT: int = 5432
    POSTGRESQL_USER: str
    REDIS_HOST: str
    REDIS_PASSWORD: str | None = None
    REDIS_PORT: int = 6379
    REDIS_USER: str | None = None

    class Config:
        case_sensitive = True

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def DATABASE_URL(self) -> str:  # noqa: N802
        """Build the database URL for PostgreSQL."""
        return f'postgresql+psycopg://{self.POSTGRESQL_USER}:{self.POSTGRESQL_PASSWORD}@{self.POSTGRESQL_HOST}:{self.POSTGRESQL_PORT}/{self.POSTGRESQL_NAME}'

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def REDIS_URL(self) -> str:  # noqa: N802
        """Build the URL for Redis."""
        url = 'redis://'

        if self.REDIS_USER:
            url += self.REDIS_USER

        if self.REDIS_PASSWORD:
            url += f':{self.REDIS_PASSWORD}@'

        return url + f'{self.REDIS_HOST}:{self.REDIS_PORT}'


settings = Settings()
