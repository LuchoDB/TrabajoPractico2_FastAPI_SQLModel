from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

from app import models  # noqa: F401  (registra las tablas)
from app.database import crear_engine, get_session
from app.dependencies import get_hoy
from app.main import app


class Reloj:
    """Fecha controlable para probar vencimientos y multas."""

    def __init__(self):
        self.hoy = date(2026, 1, 1)

    def avanzar(self, dias: int):
        self.hoy += timedelta(days=dias)


@pytest.fixture
def reloj():
    return Reloj()


@pytest.fixture
def client(reloj):
    engine = crear_engine("sqlite://")  # base en memoria
    SQLModel.metadata.create_all(engine)

    def session_de_prueba():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_de_prueba
    app.dependency_overrides[get_hoy] = lambda: reloj.hoy
    # Sin "with": no corre el lifespan, así no se toca la base real.
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def crear_autor(client):
    def _crear(nombre="Julio Cortázar", nacionalidad="Argentina"):
        r = client.post("/autores", json={"nombre": nombre, "nacionalidad": nacionalidad})
        assert r.status_code == 201
        return r.json()

    return _crear


@pytest.fixture
def crear_libro(client):
    contador = {"n": 0}

    def _crear(stock=1, isbn=None, titulo="Rayuela", anio=1963):
        contador["n"] += 1
        r = client.post(
            "/libros",
            json={
                "titulo": titulo,
                "isbn": isbn or f"978-000-{contador['n']:04d}",
                "stock": stock,
                "anio": anio,
            },
        )
        assert r.status_code == 201
        return r.json()

    return _crear


@pytest.fixture
def crear_socio(client):
    contador = {"n": 0}

    def _crear(activo=True, email=None, nombre="Ana"):
        contador["n"] += 1
        r = client.post(
            "/socios",
            json={
                "nombre": nombre,
                "email": email or f"socio{contador['n']}@mail.com",
                "activo": activo,
            },
        )
        assert r.status_code == 201
        return r.json()

    return _crear


@pytest.fixture
def prestar(client):
    def _prestar(socio_id, libro_id):
        return client.post("/prestamos", json={"socio_id": socio_id, "libro_id": libro_id})

    return _prestar
