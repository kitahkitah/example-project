class Entity:
    """Base entity with tracking of changed fields."""

    def __init__(self) -> None:
        self._changed_fields: set[str] = set()

    def __setattr__(self, key: str, value: object) -> None:
        if not key.startswith('_') and hasattr(self, '_changed_fields'):
            self._changed_fields.add(key)

        super().__setattr__(key, value)

    def get_changed_fields(self) -> set[str]:
        """Return changed fields."""
        return self._changed_fields

    def clear_changed_fields(self) -> None:
        """Clear changed fields."""
        self._changed_fields.clear()
