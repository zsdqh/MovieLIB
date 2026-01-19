from dependency_injector import providers
from fastapi import FastAPI
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.src.auth.auth.application.refresh import RefreshUseCase
from backend.src.auth.auth.domain.exceptions import InvalidTokenException
from backend.src.auth.auth.infrastructure.jwt_worker import JWTWorker
from backend.src.core.domain.exceptions import NotFoundException, UnauthorizedException
from backend.src.core.exception_handlers import exception_with_status
from backend.src.users.domain.interfaces.user_uow import IUserUnitOfWork


class RefreshMiddleware(BaseHTTPMiddleware):
    """Проверка авторизации пользователя и передача его информации внутрь запроса"""

    def __init__(
        self,
        app: FastAPI,
        user_uow: providers.Factory[IUserUnitOfWork],
        jwt_worker_provider: providers.Factory[JWTWorker],
    ):
        """
        :param app: fastapi приложение
        :param jwt_worker_provider: фабрика работников с jwt токенами
        :param public: адреса, не требующие авторизации
        """
        super().__init__(app)
        self.jwt_worker_provider = jwt_worker_provider
        self.uow_provider = user_uow

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Попытка обновить access токен, если указан refresh токен"""
        jwt_worker = self.jwt_worker_provider()
        jwt_worker.refresh_transport.set_request(request)
        jwt_worker.access_transport.set_request(request)
        request.state.use_refresh = False

        try:
            jwt_worker.get_access_token()
        except InvalidTokenException:
            try:
                jwt_worker.refresh_transport.read_token()
                request.state.use_refresh = True
            except (UnauthorizedException, AttributeError):
                pass
        response = await call_next(request)
        if request.state.use_refresh:
            try:
                jwt_worker.refresh_transport.set_response(response)
                jwt_worker.access_transport.set_response(response)
                await RefreshUseCase(jwt_worker, self.uow_provider())(
                    jwt_worker.get_refresh_token()
                )
            except UnauthorizedException as e:
                return exception_with_status(
                    status_code=status.HTTP_401_UNAUTHORIZED, exc=e
                )
            except NotFoundException:
                jwt_worker.refresh_transport.remove_token()

        return response
