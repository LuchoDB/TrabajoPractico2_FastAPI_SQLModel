from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


class SocioBase(SQLModel):
    nombre: str = Field(min_length=1)
    email: str = Field(unique=True, index=True)
    activo: bool = True


class Socio(SocioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prestamos: List["Prestamo"] = Relationship(back_populates="socio")  # noqa: F821


class SocioCreate(SQLModel):
    nombre: str = Field(min_length=1)
    email: EmailStr
    activo: bool = True


class SocioUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=1)
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None


class SocioRead(SocioBase):
    id: int
