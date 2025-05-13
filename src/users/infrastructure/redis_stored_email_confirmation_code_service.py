from __future__ import annotations

from secrets import randbelow
from typing import TYPE_CHECKING

from ..application.protocols.email_confirmation_code_service import (
    EMAIL_CONFIRMATION_CODE_TIMEOUT_SECS,
    EmailConfirmationCodeServiceValidationError,
)

if TYPE_CHECKING:
    from redis.asyncio import Redis

    from ..domain.models import UserId


class RedisStoredEmailConfirmationCodeService:
    """Email confirmation code service. Generates and verifies codes.
    Codes are stored in Redis.
    """

    CACHE_KEY_PATTERN = 'users:{user_id}:email:{email}:code'

    def __init__(self, redis_con: Redis) -> None:
        self._redis_con = redis_con

    async def generate(self, user_id: UserId, email: str) -> str:
        """Generate a code. Cache it for N mins."""
        code = str(randbelow(1_000_000)).zfill(6)

        cache_key = self.CACHE_KEY_PATTERN.format(user_id=user_id, email=email)
        await self._redis_con.set(cache_key, code, EMAIL_CONFIRMATION_CODE_TIMEOUT_SECS)

        return code

    async def verify(self, user_id: UserId, email: str, code: str) -> None:
        """Verify the received code against the cached one.
        Delete the cached code if successful.

        Raise:
            - EmailConfirmationCodeServiceValidationError, if the code isn't valid;
        """
        cache_key = self.CACHE_KEY_PATTERN.format(user_id=user_id, email=email)
        cached_code = await self._redis_con.get(cache_key)

        if not cached_code or code != cached_code:
            raise EmailConfirmationCodeServiceValidationError

        await self._redis_con.delete(cache_key)
