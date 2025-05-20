from shared.errors import ProjectError


class DisallowedToChangeError(ProjectError):
    """Update restricted fields error."""

    code = None
    detail = "It's disallowed to change departure_time, description, price when there are pessengers"


class SeatsNumberLessThanPassengersError(ProjectError):
    """Passengers number must be <= seats number."""

    code = None
    detail = 'Passengers number must be less or equal than seats number'


class RideCantBeCancelledError(ProjectError):
    """Ride has passengers and is about to start."""

    code = None
    detail = 'The ride is about to start, so it cannot be cancelled'


class CityNotFoundError(ProjectError):
    """City id doesn't exist."""

    code = None
    detail = "At least one of the specified cities wasn't found"


class ActiveRideNotFoundError(ProjectError):
    """No active ride was found."""

    code = None
    detail = "The ride doesn't exists or has already taken place"


class PriceError(ProjectError):
    """Invalid price."""

    code = None

    def __init__(self, min_value: int) -> None:
        self.detail = f'The price in this currency must be at least {min_value} units'

        super().__init__()
