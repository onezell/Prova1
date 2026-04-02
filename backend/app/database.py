from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

# Ensure data directory exists for SQLite
db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
if db_path.startswith("./"):
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
