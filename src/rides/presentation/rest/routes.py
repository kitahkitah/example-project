from fastapi import APIRouter, status

from auth import UserBearerAuth
from shared import errors as shared_errs
from shared.api.idempotency_header import IdempotencyDep
from shared.infrastructure.sqlalchemy import sessionmaker as db_sessionmaker

from ...application import use_cases as uc
from ...domain.models import OwnerId, Ride, RideId
from ...errors import ActiveRideNotFoundError
from ...infrastructure.uow import RideSQLAlchemyCityFakeUnitOfWork, RideSQLAlchemyUnitOfWork
from . import schemas

router = APIRouter()


@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.CreateRideResponse)
async def create_ride(
    body: schemas.CreateRideRequest, user_id: UserBearerAuth, idempotency: IdempotencyDep
) -> uc.CreateRideReturnDTO:
    """Create a new ride."""
    uow = RideSQLAlchemyCityFakeUnitOfWork(db_sessionmaker)
    create_ride_uc = uc.CreateRideUsecase(uow)

    price = uc.PriceDTO(**body.price.model_dump())
    route = uc.RouteDTO(**body.route.model_dump())
    ride_data = uc.CreateRideDTO(
        owner_id=OwnerId(user_id), price=price, route=route, **body.model_dump(exclude={'price', 'route'})
    )
    try:
        return await create_ride_uc.execute(ride_data)
    except shared_errs.ProjectError as err:
        raise shared_errs.APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None


@router.patch('/{ride_id}', response_model=schemas.UpdateRideResponse)
async def update_ride(
    ride_id: RideId, body: schemas.UpdateRideRequest, user_id: UserBearerAuth, idempotency: IdempotencyDep
) -> Ride:
    """Update the ride."""
    uow = RideSQLAlchemyUnitOfWork(db_sessionmaker)
    update_ride_uc = uc.UpdateRideUsecase(uow)

    body_dict = body.model_dump(exclude_unset=True)
    ride_data = uc.UpdateRideDTO(fields_to_update=tuple(body_dict.keys()), **body_dict)
    try:
        return await update_ride_uc.execute(ride_id, OwnerId(user_id), ride_data)
    except ActiveRideNotFoundError as err:
        raise shared_errs.APIError(status.HTTP_404_NOT_FOUND, err.code, err.detail) from None
    except shared_errs.ForbiddenError as err:
        raise shared_errs.APIError(status.HTTP_403_FORBIDDEN, err.code, err.detail) from None
    except shared_errs.ProjectError as err:
        raise shared_errs.APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None


@router.post('/{ride_id}/cancel', status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def cancel_ride(ride_id: RideId, user_id: UserBearerAuth) -> None:
    """Cancel the ride."""
    uow = RideSQLAlchemyUnitOfWork(db_sessionmaker)
    cancel_ride_uc = uc.CancelRideUsecase(uow)

    try:
        await cancel_ride_uc.execute(ride_id, OwnerId(user_id))
    except ActiveRideNotFoundError as err:
        raise shared_errs.APIError(status.HTTP_404_NOT_FOUND, err.code, err.detail) from None
    except shared_errs.ForbiddenError as err:
        raise shared_errs.APIError(status.HTTP_403_FORBIDDEN, err.code, err.detail) from None
    except shared_errs.ProjectError as err:
        raise shared_errs.APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None
