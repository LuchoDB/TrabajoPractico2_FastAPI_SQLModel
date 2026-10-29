import os
from typing import Iterator

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///biblioteca.db")


def crear_engine(url: str = DATABASE_URL) -> Engine:
    kwargs: dict = {}
    es_sqlite = url.startswith("sqlite")
    if es_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}
        if url in ("sqlite://", "sqlite:///:memory:"):
            # Una única conexión compartida para que la base en memoria persista.
            kwargs["poolclass"] = StaticPool
    engine = create_engine(url, **kwargs)
    if es_sqlite:

        @event.listens_for(engine, "connect")
        def _activar_claves_foraneas(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = crear_engine()


def crear_tablas(eng: Engine | None = None) -> None:
    from app import models  # noqa: F401  (registra las tablas)

    SQLModel.metadata.create_all(eng or engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
