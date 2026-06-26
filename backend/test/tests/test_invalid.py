from faker import Faker
from starlette.testclient import TestClient


class TestInvalidUsers:
    def test_register_invalid(self, test_client: TestClient, faker: Faker):
        res = test_client.post(
            url="/register",
            json={
                "username": faker.user_name(),
                "password": "123",
                "email": faker.email(),
            },
        )
        assert res.status_code == 400

    def test_me_no_login(self, test_client: TestClient):
        res = test_client.get(url="/me")
        assert res.status_code == 417

    def test_login_invalid(self, test_client: TestClient, faker: Faker):
        res = test_client.post(
            url="/login",
            json={"username": faker.user_name(), "password": faker.password()},
        )
        assert res.status_code == 404
