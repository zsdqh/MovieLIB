import pytest
from faker import Faker
from starlette.responses import Response
from starlette.testclient import TestClient



def dummy_user(faker: Faker):
    return {
        "username": faker.user_name(),
        "password": faker.password(),
        "email": faker.email(),
    }


def register_user(test_client: TestClient, single_user):
    test_client.post("/register", json=single_user)


@pytest.fixture(scope="session")
def faker() -> Faker:
    return Faker("en_us")


@pytest.fixture(scope="class")
def user_data(faker: Faker):
    return dummy_user(faker)


@pytest.fixture(scope="class", autouse=True)
def clean_tokens(test_client):
    """
    Очистка токенов клиента перед каждым классом, так как клиент имеет scope=session
    """
    test_client.cookies.clear()
    test_client.headers["Authorization"] = ""