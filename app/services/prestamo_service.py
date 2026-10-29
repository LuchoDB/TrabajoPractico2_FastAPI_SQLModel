"""Reglas de negocio de los préstamos (viven acá, no en los routers)."""
from datetime import date, timedelta
from typing import Optional, Sequence

from sqlmodel import Session, col, func, select

from app.exceptions import ConflictoError, NoEncontradoError, ProhibidoError
from app.models import Prestamo
from app.services import libro_service, socio_service

MAX_PRESTAMOS_ACTIVOS = 3
PLAZO_DIAS = 14
MULTA_POR_DIA = 100


def contar_activos(session: Session, socio_id: int) -> int:
    consulta = (
        select(func.count())
        .select_from(Prestamo)
        .where(Prestamo.socio_id == socio_id, col(Prestamo.fecha_devolucion).is_(None))
    )
    return session.exec(consulta).one()


def crear(session: Session, socio_id: int, libro_id: int, hoy: date) -> Prestamo:
    # Regla 7: recursos inexistentes -> 404
    socio = socio_service.obtener(session, socio_id)
    libro = libro_service.obtener(session, libro_id)

    # Regla 3: socio inactivo -> 403
    if not socio.activo:
        raise ProhibidoError("Un socio inactivo no puede pedir préstamos")

    # Regla 1: máximo 3 préstamos activos -> 409
    if contar_activos(session, socio_id) >= MAX_PRESTAMOS_ACTIVOS:
        raise ConflictoError(
            f"El socio ya tiene {MAX_PRESTAMOS_ACTIVOS} préstamos activos"
        )

    # Regla 2: sin stock -> 409; al prestar se descuenta 1
    if libro.stock <= 0:
        raise ConflictoError("El libro no tiene stock disponible")
    libro.stock -= 1

    # Regla 4: vencimiento = préstamo + 14 días
    prestamo = Prestamo(
        socio_id=socio_id,
        libro_id=libro_id,
        fecha_prestamo=hoy,
        fecha_vencimiento=hoy + timedelta(days=PLAZO_DIAS),
    )
    session.add(libro)
    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo


def obtener(session: Session, prestamo_id: int) -> Prestamo:
    prestamo = session.get(Prestamo, prestamo_id)
    if prestamo is None:
        raise NoEncontradoError(f"El préstamo {prestamo_id} no existe")
    return prestamo


def listar(session: Session) -> Sequence[Prestamo]:
    return session.exec(select(Prestamo).order_by(Prestamo.id)).all()


def devolver(session: Session, prestamo_id: int, hoy: date) -> Prestamo:
    prestamo = obtener(session, prestamo_id)

    # Regla 6: no se devuelve dos veces -> 409
    if prestamo.fecha_devolucion is not None:
        raise ConflictoError("El préstamo ya fue devuelto")

    # Regla 5: se repone el stock y se calcula la multa
    dias_atraso = max(0, (hoy - prestamo.fecha_vencimiento).days)
    prestamo.fecha_devolucion = hoy
    prestamo.multa = MULTA_POR_DIA * dias_atraso

    libro = libro_service.obtener(session, prestamo.libro_id)
    libro.stock += 1

    session.add(libro)
    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo


def listar_por_socio(
    session: Session, socio_id: int, activos: Optional[bool] = None
) -> Sequence[Prestamo]:
    socio_service.obtener(session, socio_id)  # 404 si no existe
    consulta = select(Prestamo).where(Prestamo.socio_id == socio_id).order_by(Prestamo.id)
    if activos is True:
        consulta = consulta.where(col(Prestamo.fecha_devolucion).is_(None))
    elif activos is False:
        consulta = consulta.where(col(Prestamo.fecha_devolucion).is_not(None))
    return session.exec(consulta).all()
