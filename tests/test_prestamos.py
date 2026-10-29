"""Un caso feliz y uno de error por cada regla de negocio."""
from datetime import date


def stock_de(client, libro_id):
    return client.get(f"/libros/{libro_id}").json()["stock"]


# ---- Regla 1: máximo 3 préstamos activos (409) ----
def test_regla1_socio_con_tres_prestamos_activos_puede_pedir_el_tercero(
    client, crear_libro, crear_socio, prestar
):
    socio = crear_socio()
    for _ in range(3):
        assert prestar(socio["id"], crear_libro()["id"]).status_code == 201


def test_regla1_cuarto_prestamo_activo_devuelve_409(client, crear_libro, crear_socio, prestar):
    socio = crear_socio()
    for _ in range(3):
        prestar(socio["id"], crear_libro()["id"])
    libro = crear_libro()
    assert prestar(socio["id"], libro["id"]).status_code == 409
    assert stock_de(client, libro["id"]) == 1  # no se descontó


def test_regla1_devolver_libera_cupo(client, crear_libro, crear_socio, prestar):
    socio = crear_socio()
    prestamos = [prestar(socio["id"], crear_libro()["id"]).json() for _ in range(3)]
    client.post(f"/prestamos/{prestamos[0]['id']}/devolucion")
    assert prestar(socio["id"], crear_libro()["id"]).status_code == 201


# ---- Regla 2: sin stock (409); al prestar se descuenta 1 ----
def test_regla2_prestar_descuenta_un_libro_del_stock(client, crear_libro, crear_socio, prestar):
    libro, socio = crear_libro(stock=2), crear_socio()
    assert prestar(socio["id"], libro["id"]).status_code == 201
    assert stock_de(client, libro["id"]) == 1


def test_regla2_libro_sin_stock_devuelve_409(client, crear_libro, crear_socio, prestar):
    libro, socio = crear_libro(stock=0), crear_socio()
    assert prestar(socio["id"], libro["id"]).status_code == 409


def test_regla2_el_ultimo_ejemplar_se_presta_una_sola_vez(
    client, crear_libro, crear_socio, prestar
):
    libro = crear_libro(stock=1)
    assert prestar(crear_socio()["id"], libro["id"]).status_code == 201
    assert prestar(crear_socio()["id"], libro["id"]).status_code == 409
    assert stock_de(client, libro["id"]) == 0


# ---- Regla 3: socio inactivo (403) ----
def test_regla3_socio_activo_puede_pedir_prestamo(client, crear_libro, crear_socio, prestar):
    assert prestar(crear_socio(activo=True)["id"], crear_libro()["id"]).status_code == 201


def test_regla3_socio_inactivo_devuelve_403(client, crear_libro, crear_socio, prestar):
    libro, socio = crear_libro(), crear_socio(activo=False)
    assert prestar(socio["id"], libro["id"]).status_code == 403
    assert stock_de(client, libro["id"]) == 1


# ---- Regla 4: plazo de 14 días ----
def test_regla4_vencimiento_es_prestamo_mas_14_dias(client, crear_libro, crear_socio, prestar, reloj):
    reloj.hoy = date(2026, 3, 1)
    p = prestar(crear_socio()["id"], crear_libro()["id"]).json()
    assert p["fecha_prestamo"] == "2026-03-01"
    assert p["fecha_vencimiento"] == "2026-03-15"
    assert p["fecha_devolucion"] is None
    assert p["multa"] == 0


def test_regla4_el_plazo_cruza_el_fin_de_mes(client, crear_libro, crear_socio, prestar, reloj):
    reloj.hoy = date(2026, 1, 25)
    p = prestar(crear_socio()["id"], crear_libro()["id"]).json()
    assert p["fecha_vencimiento"] == "2026-02-08"


# ---- Regla 5: al devolver se repone stock y se calcula la multa ----
def test_regla5_devolucion_a_tiempo_repone_stock_y_no_hay_multa(
    client, crear_libro, crear_socio, prestar, reloj
):
    libro = crear_libro(stock=1)
    p = prestar(crear_socio()["id"], libro["id"]).json()
    assert stock_de(client, libro["id"]) == 0

    reloj.avanzar(10)
    r = client.post(f"/prestamos/{p['id']}/devolucion")
    assert r.status_code == 200
    assert r.json()["multa"] == 0
    assert r.json()["fecha_devolucion"] == str(reloj.hoy)
    assert stock_de(client, libro["id"]) == 1


def test_regla5_devolver_el_dia_del_vencimiento_no_tiene_multa(
    client, crear_libro, crear_socio, prestar, reloj
):
    p = prestar(crear_socio()["id"], crear_libro()["id"]).json()
    reloj.avanzar(14)
    assert client.post(f"/prestamos/{p['id']}/devolucion").json()["multa"] == 0


def test_regla5_devolucion_tardia_cobra_100_por_dia(
    client, crear_libro, crear_socio, prestar, reloj
):
    libro = crear_libro(stock=1)
    p = prestar(crear_socio()["id"], libro["id"]).json()
    reloj.avanzar(14 + 5)  # 5 días de atraso
    r = client.post(f"/prestamos/{p['id']}/devolucion")
    assert r.status_code == 200
    assert r.json()["multa"] == 500
    assert stock_de(client, libro["id"]) == 1


def test_regla5_tambien_acepta_la_ruta_con_tilde(client, crear_libro, crear_socio, prestar):
    p = prestar(crear_socio()["id"], crear_libro()["id"]).json()
    assert client.post(f"/prestamos/{p['id']}/devolución").status_code == 200


# ---- Regla 6: no se devuelve dos veces (409) ----
def test_regla6_primera_devolucion_es_valida(client, crear_libro, crear_socio, prestar):
    p = prestar(crear_socio()["id"], crear_libro()["id"]).json()
    assert client.post(f"/prestamos/{p['id']}/devolucion").status_code == 200


def test_regla6_segunda_devolucion_devuelve_409_y_no_repone_stock_de_nuevo(
    client, crear_libro, crear_socio, prestar
):
    libro = crear_libro(stock=1)
    p = prestar(crear_socio()["id"], libro["id"]).json()
    client.post(f"/prestamos/{p['id']}/devolucion")
    assert client.post(f"/prestamos/{p['id']}/devolucion").status_code == 409
    assert stock_de(client, libro["id"]) == 1


# ---- Regla 7: recurso inexistente (404) ----
def test_regla7_prestamo_con_socio_inexistente_devuelve_404(client, crear_libro, prestar):
    assert prestar(999, crear_libro()["id"]).status_code == 404


def test_regla7_prestamo_con_libro_inexistente_devuelve_404(client, crear_socio, prestar):
    assert prestar(crear_socio()["id"], 999).status_code == 404


def test_regla7_devolver_prestamo_inexistente_devuelve_404(client):
    assert client.post("/prestamos/999/devolucion").status_code == 404


def test_regla7_obtener_prestamo_inexistente_devuelve_404(client):
    assert client.get("/prestamos/999").status_code == 404


# ---- Consultas ----
def test_listar_y_obtener_prestamos(client, crear_libro, crear_socio, prestar):
    p = prestar(crear_socio()["id"], crear_libro()["id"]).json()
    assert client.get(f"/prestamos/{p['id']}").json()["id"] == p["id"]
    assert len(client.get("/prestamos").json()) == 1
