from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.autor import Autor, AutorRead
from app.models.link import LibroAutor


class LibroBase(SQLModel):
    titulo: str = Field(min_length=1)
    isbn: str = Field(min_length=1, unique=True, index=True)
    stock: int = Field(default=0, ge=0)
    anio: int


class Libro(LibroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    autores: List[Autor] = Relationship(back_populates="libros", link_model=LibroAutor)
    prestamos: List["Prestamo"] = Relationship(back_populates="libro")  # noqa: F821


class LibroCreate(LibroBase):
    pass


class LibroUpdate(SQLModel):
    titulo: Optional[str] = Field(default=None, min_length=1)
    isbn: Optional[str] = Field(default=None, min_length=1)
    stock: Optional[int] = Field(default=None, ge=0)
    anio: Optional[int] = None


class LibroRead(LibroBase):
    id: int
    autores: List[AutorRead] = []
