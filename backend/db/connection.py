from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text
from loguru import logger
from config import settings


DATABASE_URL = settings.postgres_url.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace("postgresql+psycopg2://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    try:
        async with engine.begin() as conn:
            with open("db/migrations/001_initial.sql", "r") as f:
                sql = f.read()
            for statement in sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    await conn.execute(text(stmt))
        logger.info("Database tables verified/created.")
    except Exception as e:
        logger.error(f"Database init error: {e}")
        raise
