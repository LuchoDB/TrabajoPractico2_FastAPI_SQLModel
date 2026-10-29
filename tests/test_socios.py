def test_crud_socio(client):
    r = client.post("/socios", json={"nombre": "Ana", "email": "ana@mail.com"})
    assert r.status_code == 201
    socio = r.json()
    assert socio["activo"] is True  # por defecto

    assert client.get(f"/socios/{socio['id']}").json()["email"] == "ana@mail.com"
    assert len(client.get("/socios").json()) == 1

    r = client.put(f"/socios/{socio['id']}", json={"activo": False})
    assert r.status_code == 200 and r.json()["activo"] is False

    assert client.delete(f"/socios/{socio['id']}").status_code == 204
    assert client.get(f"/socios/{socio['id']}").status_code == 404


def test_socio_inexistente_devuelve_404(client):
    assert client.get("/socios/999").status_code == 404
    assert client.put("/socios/999", json={"nombre": "X"}).status_code == 404
    assert client.delete("/socios/999").status_code == 404
    assert client.get("/socios/999/prestamos").status_code == 404


def test_email_invalido_devuelve_422(client):
    r = client.post("/socios", json={"nombre": "Ana", "email": "no-es-un-mail"})
    assert r.status_code == 422


# Regla 8: email duplicado -> 409
def test_email_duplicado_al_crear_devuelve_409(client, crear_socio):
    crear_socio(email="dup@mail.com")
    r = client.post("/socios", json={"nombre": "Otro", "email": "dup@mail.com"})
    assert r.status_code == 409


def test_email_duplicado_al_actualizar_devuelve_409(client, crear_socio):
    crear_socio(email="a@mail.com")
    b = crear_socio(email="b@mail.com")
    assert client.put(f"/socios/{b['id']}", json={"email": "a@mail.com"}).status_code == 409


def test_actualizar_socio_con_su_propio_email_es_valido(client, crear_socio):
    socio = crear_socio(email="yo@mail.com")
    r = client.put(f"/socios/{socio['id']}", json={"email": "yo@mail.com", "nombre": "Nuevo"})
    assert r.status_code == 200 and r.json()["nombre"] == "Nuevo"


def test_no_se_puede_eliminar_socio_con_prestamos(client, crear_libro, crear_socio, prestar):
    libro, socio = crear_libro(), crear_socio()
    prestar(socio["id"], libro["id"])
    assert client.delete(f"/socios/{socio['id']}").status_code == 409


def test_prestamos_activos_del_socio(client, crear_libro, crear_socio, prestar):
    socio, otro = crear_socio(), crear_socio()
    l1, l2 = crear_libro(), crear_libro()
    p1 = prestar(socio["id"], l1["id"]).json()
    prestar(socio["id"], l2["id"])
    prestar(otro["id"], crear_libro()["id"])
    client.post(f"/prestamos/{p1['id']}/devolucion")

    todos = client.get(f"/socios/{socio['id']}/prestamos").json()
    assert len(todos) == 2

    activos = client.get(f"/socios/{socio['id']}/prestamos", params={"activos": "true"}).json()
    assert len(activos) == 1 and activos[0]["libro_id"] == l2["id"]

    devueltos = client.get(f"/socios/{socio['id']}/prestamos", params={"activos": "false"}).json()
    assert len(devueltos) == 1 and devueltos[0]["id"] == p1["id"]
