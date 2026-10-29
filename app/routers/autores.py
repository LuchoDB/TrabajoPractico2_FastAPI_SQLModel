from typing import List

from fastapi import APIRouter, Response, status

from app.dependencies import SessionDep
from app.models import AutorCreate, AutorRead, AutorUpdate
from app.services import autor_service

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.post("", response_model=AutorRead, status_code=status.HTTP_201_CREATED)
def crear_autor(datos: AutorCreate, session: SessionDep):
    return autor_service.crear(session, datos)


@router.get("", response_model=List[AutorRead])
def listar_autores(session: SessionDep):
    return autor_service.listar(session)


@router.get("/{autor_id}", response_model=AutorRead)
def obtener_autor(autor_id: int, session: SessionDep):
    return autor_service.obtener(session, autor_id)


@router.put("/{autor_id}", response_model=AutorRead)
def actualizar_autor(autor_id: int, datos: AutorUpdate, session: SessionDep):
    return autor_service.actualizar(session, autor_id, datos)


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(autor_id: int, session: SessionDep):
    autor_service.eliminar(session, autor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
