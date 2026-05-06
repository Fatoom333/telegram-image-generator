from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base


def _drop_all_tables(connection: Connection) -> None:
    Base.metadata.drop_all(bind=connection)


def _create_all_tables(connection: Connection) -> None:
    Base.metadata.create_all(bind=connection)


@pytest.fixture(scope="session")
def test_database_url() -> str:
    if settings.test_database_url is None:
        raise RuntimeError("TEST_DATABASE_URL is not configured")

    return settings.test_database_url


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_database_url: str) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        test_database_url,
        echo=False,
        pool_pre_ping=True,
    )

    async with engine.begin() as connection:
        await connection.run_sync(_drop_all_tables)
        await connection.run_sync(_create_all_tables)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(_drop_all_tables)

    await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
