from datetime import date
from typing import Annotated

from fastapi import Depends

# pyrefly: ignore[missing-import]
from sqlmodel import Session

from app.database import get_session

SessionDep = Annotated[Session, Depends(get_session)]


def get_hoy() -> date:
    """Fecha actual. Es una dependencia para poder sustituirla en los tests."""
    return date.today()


HoyDep = Annotated[date, Depends(get_hoy)]
