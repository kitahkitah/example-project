from typing import Annotated

from fastapi import APIRouter, Query, status

from auth import UserBearerAuth
from shared import errors as shared_errs
from shared.infrastructure.redis import common as common_redis
from shared.infrastructure.redis_cache import RedisCache
from shared.infrastructure.sqlalchemy import sessionmaker as db_sessionmaker
from shared.presentation.idempotency_header import IdempotencyDep

from ...application import use_cases as uc
from ...domain.models import OwnerId, PassengerId, Ride, RideId
from ...errors import ActiveRideNotFoundError
from ...infrastructure.queries.cached_sqlaclhemy_complex_ride import CachedSQLAlchemyComplexRideQuery, ComplexRideDTO
from ...infrastructure.queries.sqlalchemy_filter_rides import SQLAlchemyFilterRidesQuery
from ...infrastructure.repositories.city_fake import FakeCityRepository
from ...infrastructure.uow import RideSQLAlchemyCityFakeUnitOfWork, RideSQLAlchemyUnitOfWork
from . import schemas

router = APIRouter()


@router.get('')
async def filter_rides(params: Annotated[schemas.FilterRidesParams, Query()]) -> dict:
    """Filter rides by cities, date and available seats."""
    params_dto = uc.FilterParamsDTO(
        city_id_departure=params.city_id_departure,
        city_id_destination=params.city_id_destination,
        departure_date=params.departure_date,
        min_seats_available=params.min_seats_available,
    )

    async with db_sessionmaker() as db_session:
        query_handler = SQLAlchemyFilterRidesQuery(db_session)
        filter_rides_uc = uc.FilterRidesUsecase(query_handler)
        rides = await filter_rides_uc.execute(params_dto)

    return {'results': rides}


@router.post('', status_code=status.HTTP_201_CREATED)
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


@router.get('/{ride_id}')
async def get_complex_ride(ride_id: RideId) -> ComplexRideDTO:
    """Get full ride data along with passengers and cities data."""
    cache = RedisCache(common_redis)
    city_repo = FakeCityRepository()
    async with db_sessionmaker() as db_session:
        query_handler = CachedSQLAlchemyComplexRideQuery(db_session, cache, city_repo)
        get_ride_uc = uc.GetComplexRideUsecase(query_handler)

        try:
            return await get_ride_uc.execute(ride_id)
        except shared_errs.NotFoundError as err:
            raise shared_errs.APIError(status.HTTP_404_NOT_FOUND, err.code, err.detail) from None


@router.patch('/{ride_id}', response_model=schemas.UpdateRideResponse)
async def update_ride(
    ride_id: RideId, body: schemas.UpdateRideRequest, user_id: UserBearerAuth, idempotency: IdempotencyDep
) -> Ride:
    """Update the ride."""
    uow = RideSQLAlchemyUnitOfWork(db_sessionmaker)
    cache = RedisCache(common_redis)
    update_ride_uc = uc.UpdateRideUsecase(uow, cache)

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


@router.post('/{ride_id}/book', status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def book_ride(
    ride_id: RideId, body: schemas.BookRideRequest, user_id: UserBearerAuth, idempotency: IdempotencyDep
) -> None:
    """Book the ride."""
    uow = RideSQLAlchemyUnitOfWork(db_sessionmaker)
    cache = RedisCache(common_redis)
    book_ride_uc = uc.BookRideUsecase(uow, cache)

    try:
        await book_ride_uc.execute(ride_id, PassengerId(user_id), body.seats_booked)
    except ActiveRideNotFoundError as err:
        raise shared_errs.APIError(status.HTTP_404_NOT_FOUND, err.code, err.detail) from None
    except shared_errs.ProjectError as err:
        raise shared_errs.APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None


@router.post('/{ride_id}/cancel', status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def cancel_ride(ride_id: RideId, user_id: UserBearerAuth) -> None:
    """Cancel the ride."""
    uow = RideSQLAlchemyUnitOfWork(db_sessionmaker)
    cache = RedisCache(common_redis)
    cancel_ride_uc = uc.CancelRideUsecase(uow, cache)

    try:
        await cancel_ride_uc.execute(ride_id, OwnerId(user_id))
    except ActiveRideNotFoundError as err:
        raise shared_errs.APIError(status.HTTP_404_NOT_FOUND, err.code, err.detail) from None
    except shared_errs.ForbiddenError as err:
        raise shared_errs.APIError(status.HTTP_403_FORBIDDEN, err.code, err.detail) from None
    except shared_errs.ProjectError as err:
        raise shared_errs.APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None


@router.post('/{ride_id}/leave', status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def leave_ride(ride_id: RideId, user_id: UserBearerAuth, idempotency: IdempotencyDep) -> None:
    """Leave the ride."""
    uow = RideSQLAlchemyUnitOfWork(db_sessionmaker)
    cache = RedisCache(common_redis)
    leave_ride_uc = uc.LeaveRideUsecase(uow, cache)

    try:
        await leave_ride_uc.execute(ride_id, PassengerId(user_id))
    except ActiveRideNotFoundError as err:
        raise shared_errs.APIError(status.HTTP_404_NOT_FOUND, err.code, err.detail) from None
    except shared_errs.ProjectError as err:
        raise shared_errs.APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None
