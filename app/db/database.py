from sqlalchemy.ext.asyncio import create_async_engine

from app.core.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo = True,
    future = True,
    pool_size = 20,
    max_overflow = 30,
    pool_pre_ping = True,
    pool_recycle = 1800,
    pool_timeout = 30,

    pool_reset_on_return = "rollback",
)