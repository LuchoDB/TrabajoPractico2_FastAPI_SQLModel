from typing import List, Optional

from fastapi import APIRouter, Response, status

from app.dependencies import SessionDep
from app.models import LibroCreate, LibroRead, LibroUpdate
from app.services import libro_service

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.post("", response_model=LibroRead, status_code=status.HTTP_201_CREATED)
def crear_libro(datos: LibroCreate, session: SessionDep):
    return libro_service.crear(session, datos)


@router.get("", response_model=List[LibroRead])
def listar_libros(session: SessionDep, disponibles: Optional[bool] = None):
    """`?disponibles=true` devuelve solo los libros con stock > 0."""
    return libro_service.listar(session, disponibles)


@router.get("/{libro_id}", response_model=LibroRead)
def obtener_libro(libro_id: int, session: SessionDep):
    return libro_service.obtener(session, libro_id)


@router.put("/{libro_id}", response_model=LibroRead)
def actualizar_libro(libro_id: int, datos: LibroUpdate, session: SessionDep):
    return libro_service.actualizar(session, libro_id, datos)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(libro_id: int, session: SessionDep):
    libro_service.eliminar(session, libro_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{libro_id}/autores/{autor_id}", response_model=LibroRead)
def asociar_autor(libro_id: int, autor_id: int, session: SessionDep):
    return libro_service.asociar_autor(session, libro_id, autor_id)
