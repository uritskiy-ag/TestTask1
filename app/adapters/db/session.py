import asyncio
from contextlib import asynccontextmanager
import os
from sqlmodel import SQLModel
from sqlalchemy import func, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from domain.models import MeasurementModel, UserModel


class AsyncDatabaseHandler:
    def __init__(self):
        url = URL.create(
            drivername="postgresql+asyncpg",
            host="db",
            port=5432,
            database=os.environ["POSTGRES_DB"],
            username=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )
        self._engine = create_async_engine(
            url,
            echo=True,
            future=True,
            pool_pre_ping=True,
        )
        self._session = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def wait_for_db(self):
        retries = 10
        while retries:
            try:
                async with self._engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    return
            except OperationalError:
                retries -= 1
                await asyncio.sleep(5)
        raise RuntimeError("Не удалось подключиться к БД")

    async def create_tables(self):
        await self.wait_for_db()
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        async with self._session() as session:
            yield session

    async def close(self):
        await self._engine.dispose()


db = AsyncDatabaseHandler()

# Получаем event loop, запущенный uvicorn-ом
loop = asyncio.get_running_loop()
loop.create_task(db.create_tables())
