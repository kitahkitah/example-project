from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status

from ..infrastructure.redis import common as redis_connection

CACHE_KEY_PATTERN = 'idempotency:{key}'
IDEMPOTENCY_TIMEOUT = 60 * 2  # 2 mins


async def check_idempotency(idempotency_key: Annotated[UUID, Header()]) -> None:
    """Validate user bearer token through graphql service."""
    key = CACHE_KEY_PATTERN.format(key=idempotency_key)
    was_set = await redis_connection.set(key, 1, IDEMPOTENCY_TIMEOUT, nx=True)

    if not was_set:
        raise HTTPException(status.HTTP_425_TOO_EARLY)


IdempotencyDep = Annotated[None, Depends(check_idempotency)]
