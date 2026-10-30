from typing import Optional, Sequence

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.exceptions import ConflictoError, NoEncontradoError
from app.models import Prestamo, Socio, SocioCreate, SocioUpdate


def _verificar_email_libre(session: Session, email: str, excepto_id: Optional[int] = None) -> None:
    existente = session.exec(select(Socio).where(Socio.email == email)).first()
    if existente is not None and existente.id != excepto_id:
        raise ConflictoError(f"Ya existe un socio con el email {email}")


def crear(session: Session, datos: SocioCreate) -> Socio:
    _verificar_email_libre(session, datos.email)
    socio = Socio(nombre=datos.nombre, email=str(datos.email), activo=datos.activo)
    session.add(socio)
    try:
        session.commit()
    except IntegrityError:  # pragma: no cover
        session.rollback()
        raise ConflictoError(f"Ya existe un socio con el email {datos.email}")
    session.refresh(socio)
    return socio


def listar(session: Session) -> Sequence[Socio]:
    return session.exec(select(Socio).order_by(Socio.id)).all()


def obtener(session: Session, socio_id: int) -> Socio:
    socio = session.get(Socio, socio_id)
    if socio is None:
        raise NoEncontradoError(f"El socio {socio_id} no existe")
    return socio


def actualizar(session: Session, socio_id: int, datos: SocioUpdate) -> Socio:
    socio = obtener(session, socio_id)
    cambios = {k: v for k, v in datos.model_dump(exclude_unset=True).items() if v is not None}
    if "email" in cambios:
        cambios["email"] = str(cambios["email"])
        _verificar_email_libre(session, cambios["email"], excepto_id=socio.id)
    socio.sqlmodel_update(cambios)
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio


def eliminar(session: Session, socio_id: int) -> None:
    socio = obtener(session, socio_id)
    tiene_prestamos = session.exec(
        select(Prestamo.id).where(Prestamo.socio_id == socio_id).limit(1)
    ).first()
    if tiene_prestamos is not None:
        raise ConflictoError(
            "No se puede eliminar un socio con préstamos registrados; desactivalo en su lugar"
        )
    session.delete(socio)
    session.commit()
