from typing import List, Optional

from fastapi import APIRouter, Response, status

from app.dependencies import SessionDep
from app.models import PrestamoRead, SocioCreate, SocioRead, SocioUpdate
from app.services import prestamo_service, socio_service

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.post("", response_model=SocioRead, status_code=status.HTTP_201_CREATED)
def crear_socio(datos: SocioCreate, session: SessionDep):
    return socio_service.crear(session, datos)


@router.get("", response_model=List[SocioRead])
def listar_socios(session: SessionDep):
    return socio_service.listar(session)


@router.get("/{socio_id}", response_model=SocioRead)
def obtener_socio(socio_id: int, session: SessionDep):
    return socio_service.obtener(session, socio_id)


@router.put("/{socio_id}", response_model=SocioRead)
def actualizar_socio(socio_id: int, datos: SocioUpdate, session: SessionDep):
    return socio_service.actualizar(session, socio_id, datos)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_socio(socio_id: int, session: SessionDep):
    socio_service.eliminar(session, socio_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{socio_id}/prestamos", response_model=List[PrestamoRead])
def prestamos_del_socio(socio_id: int, session: SessionDep, activos: Optional[bool] = None):
    """`?activos=true` devuelve solo los préstamos sin devolver."""
    return prestamo_service.listar_por_socio(session, socio_id, activos)
