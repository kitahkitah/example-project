from shared.errors import ProjectError


class DisallowedToChangeError(ProjectError):
    """Update restricted fields error."""

    code = 4
    detail = "It's disallowed to change departure_time, description, price when there are pessengers"


class SeatsNumberLessThanPassengersError(ProjectError):
    """Passengers number must be <= seats number."""

    code = 5
    detail = 'The seats number must be greater or equal to the passengers number'


class RideCantBeCancelledError(ProjectError):
    """Ride has passengers and is about to start."""

    code = 6
    detail = 'The ride is about to start, so it cannot be cancelled'


class CityNotFoundError(ProjectError):
    """City id doesn't exist."""

    code = None
    detail = "At least one of the specified cities wasn't found"


class ActiveRideNotFoundError(ProjectError):
    """No active ride was found."""

    code = 7
    detail = "The ride doesn't exists or has already taken place"


class PriceError(ProjectError):
    """Invalid price."""

    code = None

    def __init__(self, min_value: int) -> None:
        self.detail = f'The price in this currency must be at least {min_value} units'

        super().__init__()


class UserAlreadyIsPassengerError(ProjectError):
    """Can't book ride twice."""

    code = 8
    detail = 'User is already a passenger of this ride'


class OwnerCantBePassengerError(ProjectError):
    """Owner can't book its own rides."""

    code = None
    detail = "The owner can't be a passenger"


class UserIsntPassengerError(ProjectError):
    """Can't leave the ride that isn't booked."""

    code = 9
    detail = "User isn't a passenger"


class RideIsFullError(ProjectError):
    """No seats available."""

    code = 10
    detail = 'The ride is full'


class SeatsBookedError(ProjectError):
    """Incorrect value."""

    code = None
    detail = 'Seats must be >= 1'
