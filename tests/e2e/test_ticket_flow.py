def _registrar_y_loguear(client, email="user@test.com", password="password123"):
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestFlujoCompletoTicket:
    def test_crear_y_listar_ticket(self, client):
        headers = _registrar_y_loguear(client)

        resp_crear = client.post(
            "/api/v1/ticket/crear",
            json={"titulo": "Mi primer ticket", "descripcion": "Prueba e2e"},
            headers=headers,
        )
        assert resp_crear.status_code == 201
        assert resp_crear.json()["estado"] == "pendiente"

        resp_listar = client.get("/api/v1/ticket/tickets", headers=headers)
        assert resp_listar.status_code == 200
        assert resp_listar.json()["total"] == 1

    def test_usuario_no_ve_tickets_ajenos_abac(self, client):
        headers_a = _registrar_y_loguear(client, email="a@test.com")
        headers_b = _registrar_y_loguear(client, email="b@test.com")

        client.post("/api/v1/ticket/crear", json={"titulo": "De A"}, headers=headers_a)

        resp = client.get("/api/v1/ticket/tickets", headers=headers_b)
        assert resp.json()["total"] == 0

    def test_no_autenticado_recibe_401(self, client):
        resp = client.post("/api/v1/ticket/crear", json={"titulo": "x"})
        assert resp.status_code == 401

    def test_fsm_rechaza_salto_de_estado_va_por_http(self, client):
        headers = _registrar_y_loguear(client)
        ticket = client.post(
            "/api/v1/ticket/crear", json={"titulo": "t"}, headers=headers
        ).json()

        resp = client.patch(
            f"/api/v1/ticket/estado/{ticket['id']}",
            json={"estado": "finalizado"},
            headers=headers,
        )
        assert resp.status_code == 400