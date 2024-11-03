from typing import TYPE_CHECKING, Any

import sqlalchemy
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker, create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.store.database import Base

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application") -> None:
        self.app = app

        self.engine: AsyncEngine | None = None
        self._db: type[DeclarativeBase] = Base
        self.session: async_sessionmaker[AsyncSession] | None = None

    async def connect(self, *args: Any, **kwargs: Any) -> None:
        self.engine = create_async_engine(
            URL.create(
                drivername="postgresql+asyncpg",
                username="kts_user",
                password="kts_pass",
                host="localhost",
                port=5432,
                database="kts"
            ), echo=True)
        self.session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def disconnect(self, *args: Any, **kwargs: Any) -> None:
        if self.engine:
            await self.engine.dispose()

    @property
    def db(self):
        return self._db
