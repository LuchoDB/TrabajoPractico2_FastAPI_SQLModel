from app.models.autor import Autor, AutorCreate, AutorRead, AutorUpdate
from app.models.libro import Libro, LibroCreate, LibroRead, LibroUpdate
from app.models.link import LibroAutor
from app.models.prestamo import Prestamo, PrestamoCreate, PrestamoRead
from app.models.socio import Socio, SocioCreate, SocioRead, SocioUpdate

__all__ = [
    "Autor", "AutorCreate", "AutorRead", "AutorUpdate",
    "Libro", "LibroCreate", "LibroRead", "LibroUpdate",
    "LibroAutor",
    "Prestamo", "PrestamoCreate", "PrestamoRead",
    "Socio", "SocioCreate", "SocioRead", "SocioUpdate",
]
