from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from users import UserId

security = HTTPBearer()


def authenticate_request(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> UserId:
    """Just a fake Bearer auth.
    Scheme: 'Bearer {user_id}'
    """
    return UserId(UUID(credentials.credentials))


UserBearerAuthDep = Annotated[UserId, Depends(authenticate_request)]
