"""Errores de negocio. Los servicios los lanzan y main.py los traduce a HTTP."""


class ErrorDeNegocio(Exception):
    def __init__(self, detalle: str):
        super().__init__(detalle)
        self.detalle = detalle


class NoEncontradoError(ErrorDeNegocio):
    """404 - el recurso no existe."""


class ConflictoError(ErrorDeNegocio):
    """409 - la operación choca con el estado actual."""


class ProhibidoError(ErrorDeNegocio):
    """403 - la operación no está permitida."""
