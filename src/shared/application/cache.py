from typing import Protocol


class Cache(Protocol):
    """A protocol for cache."""

    async def delete(self, *keys: str) -> None:
        """Delete value by key."""

    async def get(self, key: str) -> str | None:
        """Get value by key."""

    async def set(self, key: str, value: str | bytes, expires_in_secs: int) -> None:
        """Set value by key with expiration time."""
