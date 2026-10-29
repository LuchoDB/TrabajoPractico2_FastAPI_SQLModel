from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import crear_tablas
from app.exceptions import (
    ConflictoError,
    ErrorDeNegocio,
    NoEncontradoError,
    ProhibidoError,
)
from app.routers import autores, libros, prestamos, socios


@asynccontextmanager
async def lifespan(_: FastAPI):
    crear_tablas()
    yield


app = FastAPI(
    title="Sistema de Biblioteca",
    description="API REST para gestionar el catálogo de una biblioteca y sus préstamos.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(autores.router)
app.include_router(libros.router)
app.include_router(socios.router)
app.include_router(prestamos.router)

_STATUS_POR_ERROR = {
    NoEncontradoError: 404,
    ConflictoError: 409,
    ProhibidoError: 403,
}


@app.exception_handler(ErrorDeNegocio)
async def manejar_error_de_negocio(_: Request, exc: ErrorDeNegocio):
    codigo = next(
        (c for tipo, c in _STATUS_POR_ERROR.items() if isinstance(exc, tipo)), 400
    )
    return JSONResponse(status_code=codigo, content={"detail": exc.detalle})
