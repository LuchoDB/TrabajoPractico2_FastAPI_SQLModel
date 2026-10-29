def test_crud_libro(client):
    datos = {"titulo": "Ficciones", "isbn": "111", "stock": 2, "anio": 1944}
    r = client.post("/libros", json=datos)
    assert r.status_code == 201
    libro = r.json()
    assert libro["autores"] == []

    assert client.get(f"/libros/{libro['id']}").json()["titulo"] == "Ficciones"
    assert len(client.get("/libros").json()) == 1

    r = client.put(f"/libros/{libro['id']}", json={"stock": 5})
    assert r.status_code == 200 and r.json()["stock"] == 5

    assert client.delete(f"/libros/{libro['id']}").status_code == 204
    assert client.get(f"/libros/{libro['id']}").status_code == 404


def test_libro_inexistente_devuelve_404(client):
    assert client.get("/libros/999").status_code == 404
    assert client.put("/libros/999", json={"stock": 1}).status_code == 404
    assert client.delete("/libros/999").status_code == 404


def test_stock_negativo_devuelve_422(client):
    r = client.post("/libros", json={"titulo": "X", "isbn": "1", "stock": -1, "anio": 2000})
    assert r.status_code == 422
    libro = client.post(
        "/libros", json={"titulo": "X", "isbn": "2", "stock": 1, "anio": 2000}
    ).json()
    assert client.put(f"/libros/{libro['id']}", json={"stock": -5}).status_code == 422


# Regla 8: ISBN duplicado -> 409
def test_isbn_duplicado_al_crear_devuelve_409(client, crear_libro):
    crear_libro(isbn="DUP")
    r = client.post("/libros", json={"titulo": "Otro", "isbn": "DUP", "stock": 1, "anio": 2000})
    assert r.status_code == 409


def test_isbn_duplicado_al_actualizar_devuelve_409(client, crear_libro):
    crear_libro(isbn="A")
    b = crear_libro(isbn="B")
    assert client.put(f"/libros/{b['id']}", json={"isbn": "A"}).status_code == 409


def test_actualizar_libro_con_su_propio_isbn_es_valido(client, crear_libro):
    libro = crear_libro(isbn="MIO")
    r = client.put(f"/libros/{libro['id']}", json={"isbn": "MIO", "titulo": "Nuevo"})
    assert r.status_code == 200 and r.json()["titulo"] == "Nuevo"


def test_filtrar_libros_disponibles(client, crear_libro):
    con_stock = crear_libro(stock=3)
    sin_stock = crear_libro(stock=0)

    disponibles = client.get("/libros", params={"disponibles": "true"}).json()
    assert [l["id"] for l in disponibles] == [con_stock["id"]]

    agotados = client.get("/libros", params={"disponibles": "false"}).json()
    assert [l["id"] for l in agotados] == [sin_stock["id"]]

    assert len(client.get("/libros").json()) == 2


def test_asociar_autor_a_libro_y_verlo_en_la_respuesta(client, crear_autor, crear_libro):
    a1, a2 = crear_autor("Borges"), crear_autor("Bioy Casares")
    libro = crear_libro()

    r = client.post(f"/libros/{libro['id']}/autores/{a1['id']}")
    assert r.status_code == 200
    client.post(f"/libros/{libro['id']}/autores/{a2['id']}")

    autores = client.get(f"/libros/{libro['id']}").json()["autores"]
    assert {a["nombre"] for a in autores} == {"Borges", "Bioy Casares"}


def test_un_autor_puede_tener_varios_libros(client, crear_autor, crear_libro):
    autor = crear_autor()
    l1, l2 = crear_libro(), crear_libro()
    client.post(f"/libros/{l1['id']}/autores/{autor['id']}")
    client.post(f"/libros/{l2['id']}/autores/{autor['id']}")
    for l in (l1, l2):
        assert len(client.get(f"/libros/{l['id']}").json()["autores"]) == 1


def test_asociar_autor_dos_veces_no_duplica(client, crear_autor, crear_libro):
    autor, libro = crear_autor(), crear_libro()
    client.post(f"/libros/{libro['id']}/autores/{autor['id']}")
    r = client.post(f"/libros/{libro['id']}/autores/{autor['id']}")
    assert r.status_code == 200
    assert len(r.json()["autores"]) == 1


def test_asociar_con_libro_o_autor_inexistente_devuelve_404(client, crear_autor, crear_libro):
    autor, libro = crear_autor(), crear_libro()
    assert client.post(f"/libros/999/autores/{autor['id']}").status_code == 404
    assert client.post(f"/libros/{libro['id']}/autores/999").status_code == 404


def test_no_se_puede_eliminar_libro_con_prestamos(client, crear_libro, crear_socio, prestar):
    libro, socio = crear_libro(), crear_socio()
    prestar(socio["id"], libro["id"])
    assert client.delete(f"/libros/{libro['id']}").status_code == 409
