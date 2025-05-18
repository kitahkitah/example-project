from shared.errors import ProjectError


class PriceError(ProjectError):
    """Invalid price."""

    code = None

    def __init__(self, min_value: int) -> None:
        self.detail = f'The price in this currency must be at least {min_value} units'

        super().__init__()
