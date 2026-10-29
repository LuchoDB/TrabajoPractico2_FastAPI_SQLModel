from typing import List

from fastapi import APIRouter, status

from app.dependencies import HoyDep, SessionDep
from app.models import PrestamoCreate, PrestamoRead
from app.services import prestamo_service

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


@router.post("", response_model=PrestamoRead, status_code=status.HTTP_201_CREATED)
def registrar_prestamo(datos: PrestamoCreate, session: SessionDep, hoy: HoyDep):
    return prestamo_service.crear(session, datos.socio_id, datos.libro_id, hoy)


@router.get("", response_model=List[PrestamoRead])
def listar_prestamos(session: SessionDep):
    return prestamo_service.listar(session)


@router.get("/{prestamo_id}", response_model=PrestamoRead)
def obtener_prestamo(prestamo_id: int, session: SessionDep):
    return prestamo_service.obtener(session, prestamo_id)


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoRead)
@router.post("/{prestamo_id}/devolución", response_model=PrestamoRead, include_in_schema=False)
def registrar_devolucion(prestamo_id: int, session: SessionDep, hoy: HoyDep):
    """Acepta tanto `/devolucion` como `/devolución` (con tilde)."""
    return prestamo_service.devolver(session, prestamo_id, hoy)
