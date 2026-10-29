from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.link import LibroAutor

if TYPE_CHECKING:
    from app.models.libro import Libro


class AutorBase(SQLModel):
    nombre: str = Field(min_length=1)
    nacionalidad: str = Field(min_length=1)


class Autor(AutorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    libros: List["Libro"] = Relationship(back_populates="autores", link_model=LibroAutor)


class AutorCreate(AutorBase):
    pass


class AutorUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=1)
    nacionalidad: Optional[str] = Field(default=None, min_length=1)


class AutorRead(AutorBase):
    id: int
