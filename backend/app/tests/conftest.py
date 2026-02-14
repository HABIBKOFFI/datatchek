import uuid
from collections.abc import AsyncGenerator

import pytest
from cryptography.fernet import Fernet
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import config as app_config
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.utils.security import create_access_token, hash_password

# Use SQLite for tests (no PostgreSQL dependency in CI)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Generate a valid Fernet key for tests
_TEST_FERNET_KEY = Fernet.generate_key().decode()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def _set_test_encryption_key():
    """Ensure a valid Fernet key is used in all tests."""
    original = app_config.settings.ENCRYPTION_KEY
    app_config.settings.ENCRYPTION_KEY = _TEST_FERNET_KEY
    yield
    app_config.settings.ENCRYPTION_KEY = original


@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="test@datatchek.com",
        hashed_password=hash_password("TestPassword123"),
        full_name="Test User",
        company_name="DATATCHEK",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}
