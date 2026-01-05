from typing import Any

from dependency_injector import providers
from fastapi import FastAPI
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.src.auth.auth.domain.exceptions import InvalidTokenException
from backend.src.auth.auth.infrastructure.jwt_worker import JWTWorker
from backend.src.core.domain.exceptions import UnauthorizedException
from backend.src.core.exception_handlers import exception_with_status


def fetch_url_path(request: Request) -> str:
    """Получение пути без версии"""
    return request.url.path.replace("/v1", "")


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Проверка авторизации пользователя и передача его информации внутрь запроса"""

    def __init__(
        self,
        app: FastAPI,
        jwt_worker_provider: providers.Factory[JWTWorker],
        public: list[str] | None = None,
    ):
        """
        :param app: fastapi приложение
        :param jwt_worker_provider: фабрика работников с jwt токенами
        :param public: адреса, не требующие авторизации
        """
        if not public:
            public = ["/login", "/register", "/docs", "/openapi.json", "/refresh", "/"]
        super().__init__(app)
        self.jwt_worker_provider = jwt_worker_provider
        self.public = public

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Считывание данных о пользователе и передача их в запрос"""
        jwt_worker = self.jwt_worker_provider()
        url = fetch_url_path(request)
        jwt_worker.refresh_transport.set_request(request)
        jwt_worker.access_transport.set_request(request)

        try:
            token_data: Any = None

            if url == "/refresh":
                token_data = jwt_worker.get_refresh_token()

            if url not in self.public and not url.startswith("/static"):
                if request.state.use_refresh:
                    token_data = jwt_worker.get_refresh_token()
                else:
                    token_data = jwt_worker.get_access_token()

            request.state.user = token_data

        except InvalidTokenException as e:
            return exception_with_status(
                status_code=status.HTTP_417_EXPECTATION_FAILED, exc=e
            )
        except UnauthorizedException as e:
            return exception_with_status(
                status_code=status.HTTP_401_UNAUTHORIZED, exc=e
            )
        response = await call_next(request)
        return response
