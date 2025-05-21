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


class UserAlreadyIsPassengerError(ProjectError):
    """Can't book ride twice."""

    code = None
    detail = 'User is already a passenger of this ride'


class OwnerCantBePassengerError(ProjectError):
    """Owner can't book its own rides."""

    code = None
    detail = "The owner can't be a passenger"


class UserIsntPassengerError(ProjectError):
    """Can't leave the ride that isn't booked."""

    code = None
    detail = "User isn't a passenger of this ride"


class RideIsFullError(ProjectError):
    """No seats available."""

    code = None
    detail = 'The ride is full'


class SeatsBookedError(ProjectError):
    """Incorrect value."""

    code = None
    detail = 'Seats must be >= 1'
