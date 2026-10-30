from typing import Optional, Sequence

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.exceptions import ConflictoError, NoEncontradoError
from app.models import Libro, LibroCreate, LibroUpdate, Prestamo
from app.services import autor_service


def _verificar_isbn_libre(session: Session, isbn: str, excepto_id: Optional[int] = None) -> None:
    existente = session.exec(select(Libro).where(Libro.isbn == isbn)).first()
    if existente is not None and existente.id != excepto_id:
        raise ConflictoError(f"Ya existe un libro con ISBN {isbn}")


def crear(session: Session, datos: LibroCreate) -> Libro:
    _verificar_isbn_libre(session, datos.isbn)
    libro = Libro.model_validate(datos)
    session.add(libro)
    try:
        session.commit()
    except IntegrityError:  # pragma: no cover
        session.rollback()
        raise ConflictoError(f"Ya existe un libro con ISBN {datos.isbn}")
    session.refresh(libro)
    return libro


def listar(session: Session, disponibles: Optional[bool] = None) -> Sequence[Libro]:
    consulta = select(Libro).order_by(Libro.id)
    if disponibles is True:
        consulta = consulta.where(Libro.stock > 0)
    elif disponibles is False:
        consulta = consulta.where(Libro.stock == 0)
    return session.exec(consulta).all()


def obtener(session: Session, libro_id: int) -> Libro:
    libro = session.get(Libro, libro_id)
    if libro is None:
        raise NoEncontradoError(f"El libro {libro_id} no existe")
    return libro


def actualizar(session: Session, libro_id: int, datos: LibroUpdate) -> Libro:
    libro = obtener(session, libro_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "isbn" in cambios and cambios["isbn"] is not None:
        _verificar_isbn_libre(session, cambios["isbn"], excepto_id=libro.id)
    # Un None explícito no puede pisar campos obligatorios.
    cambios = {k: v for k, v in cambios.items() if v is not None}
    libro.sqlmodel_update(cambios)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


def eliminar(session: Session, libro_id: int) -> None:
    libro = obtener(session, libro_id)
    tiene_prestamos = session.exec(
        select(Prestamo.id).where(Prestamo.libro_id == libro_id).limit(1)
    ).first()
    if tiene_prestamos is not None:
        raise ConflictoError("No se puede eliminar un libro con préstamos registrados")
    libro.autores.clear()
    session.delete(libro)
    session.commit()


def asociar_autor(session: Session, libro_id: int, autor_id: int) -> Libro:
    """Asocia un autor a un libro. Es idempotente: repetirlo no duplica."""
    libro = obtener(session, libro_id)
    autor = autor_service.obtener(session, autor_id)
    if autor not in libro.autores:
        libro.autores.append(autor)
        session.add(libro)
        session.commit()
        session.refresh(libro)
    return libro
