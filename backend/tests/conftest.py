import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import delete
from httpx import AsyncClient, ASGITransport

import app.core.database as db_module
from app.core.config import settings
from app.core.database import get_db
import app.main as main_module
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.password_reset_token import PasswordResetToken
from app.models.auth_log import AuthLog
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis, ParsingMetric
from app.models.candidate_profile import CandidateProfile, ProfileCompleteness, ProfileUpdate

# Thiết lập engine và session factory sử dụng NullPool cho quá trình chạy test
db_module.engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool
)

db_module.async_session_factory = async_sessionmaker(
    bind=db_module.engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Cập nhật tham chiếu local để dùng đúng engine mới
engine = db_module.engine
async_session_factory = db_module.async_session_factory

@pytest.fixture(scope="session")
def event_loop():
    """Tạo một event loop duy nhất cho toàn bộ session test."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def dispose_engine():
    """Đóng engine khi kết thúc test session."""
    yield
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Tạo AsyncSession cho mỗi test case."""
    async with async_session_factory() as session:
        yield session

@pytest_asyncio.fixture(autouse=True)
async def cleanup_db():
    """Tự động làm sạch dữ liệu sau mỗi test case."""
    yield
    async with async_session_factory() as session:
        async with session.begin():
            await session.execute(delete(ProfileUpdate))
            await session.execute(delete(ProfileCompleteness))
            await session.execute(delete(CandidateProfile))
            await session.execute(delete(ParsingMetric))
            await session.execute(delete(ResumeAnalysis))
            await session.execute(delete(Resume))
            await session.execute(delete(AuthLog))
            await session.execute(delete(PasswordResetToken))
            await session.execute(delete(RefreshToken))
            await session.execute(delete(User))

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Tạo httpx AsyncClient để gửi request giả lập tới FastAPI."""
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    main_module.app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=main_module.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
        
    main_module.app.dependency_overrides.clear()
