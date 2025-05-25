from redis.asyncio import Redis


class RedisCache:
    """Redis implementation of Cache protocol."""

    def __init__(self, connection: Redis) -> None:
        self._con = connection

    async def delete(self, *keys: str) -> None:
        """Delete value by key."""
        await self._con.delete(*keys)

    async def get(self, key: str) -> str | None:
        """Get value by key."""
        return await self._con.get(key)  # type: ignore[no-any-return]

    async def set(self, key: str, value: str | bytes, expires_in_secs: int) -> None:
        """Set value by key with expiration time."""
        await self._con.set(key, value, expires_in_secs)
