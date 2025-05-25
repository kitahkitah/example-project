from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings
from .logging import logger

if settings.DEBUG:
    engine = create_async_engine(
        settings.DATABASE_URL, pool_size=3, max_overflow=1, pool_recycle=1800, echo=settings.DEBUG
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL, pool_size=10, max_overflow=5, pool_recycle=1800, echo=settings.DEBUG
    )

sessionmaker = async_sessionmaker(autoflush=False, expire_on_commit=False, bind=engine)


if settings.DEBUG:

    @event.listens_for(engine.sync_engine, 'before_cursor_execute')
    def explain_all_queries(conn, cursor, statement, parameters, context, executemany):  # type: ignore[no-untyped-def]
        """EXPLAIN all queries."""
        stmt_lower = statement.lstrip().upper()
        if stmt_lower.startswith('EXPLAIN'):
            return

        raw_cursor = conn.connection.cursor()
        try:
            raw_cursor.execute('EXPLAIN ' + statement, parameters or ())
            plan_rows = raw_cursor.fetchall()
        finally:
            raw_cursor.close()

        logger.info('\n'.join(str(row) for row in plan_rows))


class Base(DeclarativeBase):
    """Base class for all models."""
