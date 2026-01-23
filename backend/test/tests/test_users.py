import pytest
from faker import Faker
from starlette.testclient import TestClient

from backend.test.common import user_data


class TestUsers:
    """Тестирование эндпоинтов пользователей"""
    @pytest.mark.dependency(name="register")
    def test_register(self, test_client: TestClient, user_data) -> None:
        res = test_client.post(
            url="/register",
            json=user_data,
        )
        assert res.status_code == 200

    @pytest.mark.dependency(depends=["register"], name="login")
    def test_login(self, test_client: TestClient, user_data):
        res = test_client.post(url="/login", json=user_data)
        assert res.status_code == 200

    @pytest.mark.dependency(depends=["login"])
    def test_me(self, test_client, user_data):
        res = test_client.get(
            url="/me",
        )
        body = str(res.content)
        assert "id" in body
        assert (
            user_data["username"] in body
            and user_data["email"] in body
        )

    @pytest.mark.dependency(depends=["register"])
    def test_create_the_same(self, test_client: TestClient, faker: Faker, user_data):
        res = test_client.post(
            "/register",
            json={
                "username": user_data["username"],
                "password": faker.password(),
                "email": faker.email(),
            },
        )
        assert (
            res.json().get("detail") == "Имя пользователя уже используется"
            and res.status_code == 409
        )
        res = test_client.post(
            "/register",
            json={
                "username": faker.user_name(),
                "password": faker.password(),
                "email": user_data["email"],
            },
        )
        assert (
            res.json().get("detail") == "Почта уже используется"
            and res.status_code == 409
        )

    @pytest.mark.dependency(depends=["register"])
    def test_wrong_password(self, test_client: TestClient, faker: Faker, user_data):
        res = test_client.post(
            "/login",
            json={"username": user_data["username"], "password": faker.password()},
        )
        assert res.json().get("detail") == "Неверный пароль"

    @pytest.mark.dependency(depends=["login"])
    def test_change_user_info(self, test_client: TestClient, faker: Faker):
        new_email = faker.email()
        res = test_client.patch("/me", json={"email": new_email})
        res = test_client.get(url="/me")
        assert new_email in str(res.content)

    @pytest.mark.dependency(depends=["login"])
    def test_user_permission(self, test_client):
        res = test_client.get("/users")
        assert res.status_code == 403

    @pytest.mark.dependency(depends=["login"])
    def test_email_not_activated(self, test_client):
        res = test_client.get("/roles")
        assert res.status_code == 403 and "not confirmed" in res.json()["detail"]