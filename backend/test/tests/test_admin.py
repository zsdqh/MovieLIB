import asyncio
import multiprocessing

import pytest

from backend.src.auth.confirmations.domain.entities import Confirmation as ConfData
from backend.src.auth.confirmations.infrastructure.db.orm import Confirmation
from backend.src.users.presentation.create_superuser import create_superuser
from backend.test.common import dummy_user, register_user


def run_create_superuser(user_data, container):
    asyncio.run(
        create_superuser(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
            uow=container.user_uow(),
            pwd_hasher=container.password_hasher(),
            list_uow=container.list_uow()
        )
    )


class TestAdmin:
    @pytest.mark.dependency(name="create")
    def test_create_superuser(self, user_data, container):
        """
        Костыльный тест, запускающий создание суперпользователя
        в другом процессе для того, чтобы существующий event loop не ломался
        из-за асинхронной функции создания суперпользователя

        В реальных условиях создание суперпользователя и так происходит
        всегда в отдельном процессе через консольную команду
        """
        p = multiprocessing.Process(
            target=run_create_superuser, args=(user_data, container)
        )
        p.start()
        p.join()
        assert p.exitcode == 0

    @pytest.mark.dependency(name="login", depends=["create"])
    def test_login_superuser(self, user_data, test_client):
        res = test_client.post(url="/login", json=user_data)
        assert res.status_code == 200

    @pytest.mark.dependency(name="activated", depends=["login"])
    def test_activation(self, user_data, test_client, db_connection, faker):
        res = test_client.get("/send_confirmation")
        code = db_connection.get(Confirmation, res.json()["id"]).token
        assert len(code) == 4
        res = test_client.get(f"/confirm_email?code={faker.random_letters(10)}")
        assert res.status_code == 400
        res = test_client.get(f"/confirm_email?code={code}")
        assert res.status_code == 200 and "Почта подтверждена" in res.text
        res = test_client.get("/refresh")
        assert res.status_code == 200

    @pytest.mark.dependency(depends=["activated"])
    def test_user_list(self, test_client):
        res = test_client.get("/admin/users")
        assert res.status_code == 200 and isinstance(res.json(), list)

    @pytest.mark.dependency(depends=["activated"])
    def test_user_list_pagination(self, test_client, faker):
        for _ in range(5):
            register_user(test_client, dummy_user(faker))
        res = test_client.get("/admin/users")
        # админ + 5 новых пользователей
        assert len(res.json()) >= 6
        res = test_client.get("/admin/users?size=2&page=1")
        assert len(res.json()) == 2
        res = test_client.get("/admin/users?order_by=created_at")
        sorted_ = res.json()
        res = test_client.get("/admin/users?order_by=-created_at")
        assert sorted_ == res.json()[::-1]

    @pytest.mark.dependency(depends=["activated"])
    def test_change_password(self, test_client, faker, redis_client):
        res = test_client.get("/send_password_confirmation")
        code = ConfData.model_validate_json(redis_client.get(res.json()["id"])).token
        new_password = faker.password()
        res = test_client.post(
            f"/change_password?code={faker.random_letters(6)}",
            json={"password": new_password},
        )
        assert res.status_code == 400
        res = test_client.post(
            f"/change_password?code={code}", json={"password": new_password}
        )
        assert res.status_code == 200
        res = test_client.post(
            "/login",
            json={"username": res.json()["username"], "password": new_password},
        )
        assert res.status_code == 200
