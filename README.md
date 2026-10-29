# Sistema de Biblioteca (FastAPI + SQLModel)

API REST para gestionar el catálogo de una biblioteca (autores, libros, socios) y sus préstamos, con reglas de negocio y códigos HTTP correctos.

## Estructura

```
app/
├── main.py            # app FastAPI + traducción de errores de negocio a HTTP
├── database.py        # engine y sesión (SQLite)
├── dependencies.py    # SessionDep y get_hoy (fecha actual, reemplazable en tests)
├── exceptions.py      # NoEncontradoError (404), ConflictoError (409), ProhibidoError (403)
├── models/            # tablas SQLModel + esquemas Create/Update/Read
├── routers/           # endpoints (solo HTTP, sin lógica de negocio)
└── services/          # reglas de negocio
tests/                 # pytest con base en memoria
```

## Cómo correrlo

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs
- La base es SQLite (`biblioteca.db`, se crea sola). Para usar otra: variable de entorno `DATABASE_URL`.

## Cómo testearlo

```bash
pip install -r requirements-dev.txt
pytest
```

`pytest.ini` ya incluye la cobertura y falla si baja del 80 %. Los tests usan una base SQLite **en memoria** y una fecha controlable, por lo que no tocan `biblioteca.db` ni dependen del día en que se corran.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST / GET / GET / PUT / DELETE | `/autores`, `/autores/{id}` | CRUD de autores |
| POST / GET / GET / PUT / DELETE | `/libros`, `/libros/{id}` | CRUD de libros (la respuesta incluye sus autores) |
| POST / GET / GET / PUT / DELETE | `/socios`, `/socios/{id}` | CRUD de socios |
| POST | `/libros/{id}/autores/{autor_id}` | Asocia un autor a un libro (idempotente) |
| GET | `/libros?disponibles=true` | Libros con stock > 0 (`false`: sin stock) |
| POST | `/prestamos` | Registra un préstamo (`{"socio_id": 1, "libro_id": 1}`) |
| POST | `/prestamos/{id}/devolucion` | Registra una devolución (también acepta `/devolución`) |
| GET | `/socios/{id}/prestamos?activos=true` | Préstamos activos del socio |
| GET | `/prestamos`, `/prestamos/{id}` | Consulta de préstamos |

`PUT` acepta campos parciales: solo se modifican los que se envían.

## Reglas de negocio

| # | Regla | Error |
|---|---|---|
| 1 | Un socio no puede tener más de 3 préstamos activos | 409 |
| 2 | No se presta un libro sin stock; al prestar se descuenta 1 | 409 |
| 3 | Un socio inactivo no puede pedir préstamos | 403 |
| 4 | `fecha_vencimiento = fecha_prestamo + 14 días` | — |
| 5 | Al devolver se repone el stock y la multa es $100 × días de atraso (0 si llegó a tiempo) | — |
| 6 | No se puede devolver un préstamo ya devuelto | 409 |
| 7 | Recurso inexistente | 404 |
| 8 | ISBN o email duplicado | 409 |

Todas viven en `app/services/prestamo_service.py` (préstamos) y en los servicios de libros y socios (duplicados). Orden de validación al prestar: existencia (404) → socio activo (403) → tope de 3 (409) → stock (409).

## Decisiones de diseño

- **Reglas en servicios:** los routers solo reciben y responden; los servicios lanzan excepciones de negocio que `main.py` convierte en 403/404/409.
- **Fecha inyectable:** `get_hoy` es una dependencia, así los tests pueden simular el paso del tiempo para probar vencimientos y multas.
- **Integridad:** no se puede eliminar un libro o socio con préstamos registrados (409). Al eliminar un autor se quitan sus asociaciones con libros.
- **Multa:** entero en pesos.
