import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel

from app.main import app
from app.core.db import get_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    test_db_url = f"sqlite+aiosqlite:///:memory:"
    engine_test = create_async_engine(test_db_url)
    
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    TestingSessionLocal = async_sessionmaker(
        bind=engine_test, 
        class_=AsyncSession, 
        expire_on_commit=False
    )

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
    await engine_test.dispose()
