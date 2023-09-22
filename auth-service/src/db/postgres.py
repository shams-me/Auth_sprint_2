from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

session_maker: async_sessionmaker | None = None


async def get_postgres_session() -> AsyncSession:
    async with session_maker() as session:
        yield session
