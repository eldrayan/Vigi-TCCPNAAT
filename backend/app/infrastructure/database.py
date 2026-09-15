"""
Descrição: Configura o engine e as sessões assíncronas do banco de dados SQLite.
Autor: Leôncio Ferreira
"""

from collections.abc import AsyncIterator

from sqlalchemy import event
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()


def ensure_sqlite_directory(database_url: str) -> None:
    """
    Descrição: Cria o diretório pai quando o banco SQLite usa arquivo local.
    Autor: Leôncio Ferreira
    """
    url = make_url(database_url)
    if url.get_backend_name() != "sqlite" or not url.database:
        return
    if url.database == ":memory:" or url.database.startswith("file:"):
        return
    from pathlib import Path

    Path(url.database).parent.mkdir(parents=True, exist_ok=True)


class Base(DeclarativeBase):
    pass


ensure_sqlite_directory(settings.database_url)
engine = create_async_engine(settings.database_url)


@event.listens_for(engine.sync_engine, "connect")
def configure_sqlite(connection, connection_record) -> None:
    cursor = connection.cursor()
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA busy_timeout = 5000")
    cursor.close()


SessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionFactory() as session:
        yield session
