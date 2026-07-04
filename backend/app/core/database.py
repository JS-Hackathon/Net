from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Create async engine with pooling configured if not SQLite
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine_kwargs = {
    "echo": True if settings.ENV == "development" else False,
}
if not is_sqlite:
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 20,
        "max_overflow": 10,
    })

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,  # verbose SQL logging is opt-in (SQL_ECHO=true)
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    **engine_kwargs
)


# Async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for SQLAlchemy ORM models
class Base(DeclarativeBase):
    pass

# Dependency to get DB session
async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
