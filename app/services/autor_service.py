from typing import Sequence

from sqlmodel import Session, select

from app.exceptions import NoEncontradoError
from app.models import Autor, AutorCreate, AutorUpdate


def crear(session: Session, datos: AutorCreate) -> Autor:
    autor = Autor.model_validate(datos)
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


def listar(session: Session) -> Sequence[Autor]:
    return session.exec(select(Autor).order_by(Autor.id)).all()


def obtener(session: Session, autor_id: int) -> Autor:
    autor = session.get(Autor, autor_id)
    if autor is None:
        raise NoEncontradoError(f"El autor {autor_id} no existe")
    return autor


def actualizar(session: Session, autor_id: int, datos: AutorUpdate) -> Autor:
    autor = obtener(session, autor_id)
    autor.sqlmodel_update(datos.model_dump(exclude_unset=True))
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


def eliminar(session: Session, autor_id: int) -> None:
    autor = obtener(session, autor_id)
    autor.libros.clear()  # borra las filas de la tabla intermedia
    session.delete(autor)
    session.commit()
