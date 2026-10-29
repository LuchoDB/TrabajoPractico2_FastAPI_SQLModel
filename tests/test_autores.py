def test_crud_autor(client):
    r = client.post("/autores", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    assert r.status_code == 201
    autor = r.json()
    assert autor["id"] and autor["nombre"] == "Borges"

    assert client.get(f"/autores/{autor['id']}").json()["nacionalidad"] == "Argentina"
    assert len(client.get("/autores").json()) == 1

    r = client.put(f"/autores/{autor['id']}", json={"nacionalidad": "AR"})
    assert r.status_code == 200
    assert r.json()["nacionalidad"] == "AR"
    assert r.json()["nombre"] == "Borges"  # no tocado

    assert client.delete(f"/autores/{autor['id']}").status_code == 204
    assert client.get(f"/autores/{autor['id']}").status_code == 404


def test_autor_inexistente_devuelve_404(client):
    assert client.get("/autores/999").status_code == 404
    assert client.put("/autores/999", json={"nombre": "X"}).status_code == 404
    assert client.delete("/autores/999").status_code == 404


def test_autor_con_datos_invalidos_devuelve_422(client):
    assert client.post("/autores", json={"nombre": ""}).status_code == 422


def test_eliminar_autor_lo_quita_de_sus_libros(client, crear_autor, crear_libro):
    autor, libro = crear_autor(), crear_libro()
    client.post(f"/libros/{libro['id']}/autores/{autor['id']}")
    assert client.delete(f"/autores/{autor['id']}").status_code == 204
    assert client.get(f"/libros/{libro['id']}").json()["autores"] == []
