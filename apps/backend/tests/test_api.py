from fastapi.testclient import TestClient

from tests.conftest import login


def test_normal_user_cannot_access_admin(client: TestClient) -> None:
    login(client, "ana@example.com", "password-user1")
    response = client.get("/admin/usuarios")
    assert response.status_code == 403


def test_chat_filters_strict_rating_and_records_usage(client: TestClient) -> None:
    login(client, "ana@example.com", "password-user1")
    response = client.post(
        "/chat/preguntar",
        json={
            "categoria": "videojuegos",
            "pregunta": "¿Qué juegos de disparos tienen una calificación mayor a 8.5?",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert [row["titulo"] for row in body["fuentes"]["videojuegos"]] == ["DOOM Test"]
    assert body["consumo_palabras"] > 0
    history = client.get("/historial").json()
    assert history["total"] == 1
    assert history["items"][0]["pregunta"].startswith("¿Qué juegos")
    usage = client.get("/consumo/resumen").json()
    assert usage["total"] == body["consumo_palabras"]
    assert usage["items"][1]["tokens"] == body["consumo_palabras"]


def test_history_is_isolated_by_authenticated_user(client: TestClient) -> None:
    login(client, "ana@example.com", "password-user1")
    client.post(
        "/chat/preguntar", json={"categoria": "peliculas", "pregunta": "Dame una película de drama"}
    )
    client.post("/auth/logout")
    login(client, "beto@example.com", "password-user2")
    response = client.get("/historial")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_last_admin_cannot_remove_own_account(client: TestClient) -> None:
    login(client, "admin@example.com", "password-admin")
    me = client.get("/auth/me").json()
    response = client.delete(f"/admin/usuarios/{me['id_usuario']}")
    assert response.status_code == 409


def test_invalid_origin_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        headers={"Origin": "https://evil.example"},
        json={"correo": "ana@example.com", "password": "password-user1"},
    )
    assert response.status_code == 403
