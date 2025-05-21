from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

from rides.presentation.rest.routes import router as rides_router
from shared.infrastructure.config import settings
from shared.infrastructure.redis import connections as redis_connections
from users.presentation.rest.routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Actions on shutdown:
    - Close Redis connections;
    """
    yield

    for redis_con in redis_connections:
        await redis_con.aclose()


app = FastAPI(
    default_response_class=ORJSONResponse,
    docs_url=None if not settings.DEBUG else '/docs',
    lifespan=lifespan,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=['*'],
    allow_methods=['*'],
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
)
app.add_middleware(GZipMiddleware)

app.include_router(users_router, prefix='/api/v1/users')
app.include_router(rides_router, prefix='/api/v1/rides')
