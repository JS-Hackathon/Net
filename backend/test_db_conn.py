import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def try_connect(url):
    print(f"Trying to connect to {url} ...")
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        print("SUCCESS!")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

async def main():
    urls = [
        "postgresql+asyncpg://postgres:@localhost:5432/postgres",
        "postgresql+asyncpg://postgres:123@localhost:5432/postgres",
        "postgresql+asyncpg://postgres:1234@localhost:5432/postgres",
        "postgresql+asyncpg://postgres:12345@localhost:5432/postgres",
        "postgresql+asyncpg://postgres:admin@localhost:5432/postgres",
        "postgresql+asyncpg://postgres:root@localhost:5432/postgres",
        "postgresql+asyncpg://postgres:123456@localhost:5432/postgres",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        "postgresql+asyncpg://root:@localhost:5432/postgres",
        "postgresql+asyncpg://root:root@localhost:5432/postgres",
        "postgresql+asyncpg://root:123456@localhost:5432/postgres"
    ]

    for url in urls:
        if await try_connect(url):
            print(f"\nWorks with: {url}")
            break

if __name__ == "__main__":
    asyncio.run(main())
