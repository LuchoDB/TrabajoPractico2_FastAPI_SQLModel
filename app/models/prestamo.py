from datetime import date
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.libro import Libro
from app.models.socio import Socio


class PrestamoBase(SQLModel):
    socio_id: int = Field(foreign_key="socio.id")
    libro_id: int = Field(foreign_key="libro.id")


class Prestamo(PrestamoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: Optional[date] = None
    multa: int = 0

    socio: Optional[Socio] = Relationship(back_populates="prestamos")
    libro: Optional[Libro] = Relationship(back_populates="prestamos")


class PrestamoCreate(SQLModel):
    socio_id: int
    libro_id: int


class PrestamoRead(PrestamoBase):
    id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: Optional[date] = None
    multa: int = 0
