from fastapi import APIRouter, status

from auth import UserBearerAuth
from shared.api.idempotency_header import IdempotencyDep
from shared.errors import APIError, ProjectError
from shared.infrastructure.config import settings
from shared.infrastructure.logging import logger
from shared.infrastructure.redis import common as common_redis
from shared.infrastructure.sqlalchemy import sessionmaker as db_sessionmaker

from ...application import use_cases as uc
from ...domain.models import User, UserId
from ...infrastructure.mail_service import FakeMailClient
from ...infrastructure.redis_stored_email_confirmation_code_service import RedisStoredEmailConfirmationCodeService
from ...infrastructure.uow import UserSQLAlchemyUnitOfWork
from . import schemas

router = APIRouter()


@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.CreateUserResponse)
async def create_user(body: schemas.CreateUserRequest) -> User:
    """Create a new user."""
    user_data = uc.CreateUserDTO(**body.model_dump())
    async with UserSQLAlchemyUnitOfWork(common_redis, db_sessionmaker) as uow:
        create_user_uc = uc.CreateUserUsecase(uow)

        try:
            return await create_user_uc.execute(user_data)
        except ProjectError as err:
            raise APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None


@router.get('/me', response_model=schemas.GetOwnProfileResponse)
async def get_own_profile(user_id: UserBearerAuth) -> User:
    """Get the requesting user data."""
    async with UserSQLAlchemyUnitOfWork(common_redis, db_sessionmaker) as uow:
        get_user_uc = uc.GetUserUsecase(uow)
        return await get_user_uc.execute(user_id)


@router.patch('/me', response_model=schemas.GetOwnProfileResponse)
async def update_user(user_id: UserBearerAuth, body: schemas.UpdateUserRequest) -> User:
    """Update user data."""
    body_dict = body.model_dump(exclude_unset=True)
    user_data = uc.UpdateUserDTO(fields_to_update=tuple(body_dict.keys()), **body_dict)

    async with UserSQLAlchemyUnitOfWork(common_redis, db_sessionmaker) as uow:
        update_user_uc = uc.UpdateUserUsecase(uow)

        try:
            return await update_user_uc.execute(user_id, user_data)
        except ProjectError as err:
            raise APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None


@router.post('/me/confirm-email', status_code=status.HTTP_204_NO_CONTENT)
async def confirm_email(user_id: UserBearerAuth, body: schemas.ConfirmEmailRequest) -> None:
    """Confirm email with OTP code."""
    async with UserSQLAlchemyUnitOfWork(common_redis, db_sessionmaker) as uow:
        code_service = RedisStoredEmailConfirmationCodeService(common_redis)
        confirm_email_uc = uc.ConfirmEmailUsecase(uow, code_service)

        try:
            await confirm_email_uc.execute(user_id, body.code)
        except ProjectError as err:
            raise APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None


@router.post('/me/send-confirmation-mail', status_code=status.HTTP_204_NO_CONTENT)
async def send_confirmation_mail(user_id: UserBearerAuth, idempotency: IdempotencyDep) -> None:
    """Send OTP code for email confirmation via mail."""
    async with UserSQLAlchemyUnitOfWork(common_redis, db_sessionmaker) as uow:
        code_service = RedisStoredEmailConfirmationCodeService(common_redis)
        mail_client = FakeMailClient(logger)
        mail_uc = uc.SendEmailConfirmationCodeUsecase(uow, code_service, mail_client, settings.EMAIL_FROM)

        try:
            await mail_uc.execute(user_id)
        except ProjectError as err:
            raise APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None


@router.get('/{user_id}', response_model=schemas.GetUserResponse)
async def get_user(user_id: UserId) -> User:
    """Get user data."""
    async with UserSQLAlchemyUnitOfWork(common_redis, db_sessionmaker) as uow:
        get_user_uc = uc.GetUserUsecase(uow)

        try:
            return await get_user_uc.execute(user_id)
        except ProjectError as err:
            raise APIError(status.HTTP_400_BAD_REQUEST, err.code, err.detail) from None
