from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.src.core.domain.exceptions import (
    AccessDeniedException,
    AlreadyExistsException,
    BadRequestException,
    DomainException,
    NotFoundException,
    UnauthorizedException,
)


def exception_with_status(status_code: int, exc: DomainException) -> JSONResponse:
    """Превращение Domain ошибки в JSON ответ"""
    return JSONResponse(status_code=status_code, content={"detail": exc.detail})


def register_exception_handlers(app: FastAPI) -> None:
    """Создание обработчиков ошибок для их корректного вывода пользователю"""

    @app.exception_handler(DomainException)
    async def handle_server_exception(
        request: Request, exc: DomainException
    ) -> JSONResponse:
        """Внутренние ошибки сервера(неизвестные) с 500 кодом"""
        return exception_with_status(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, exc=exc
        )

    @app.exception_handler(BadRequestException)
    async def handle_bad_request_exception(
        request: Request, exc: BadRequestException
    ) -> JSONResponse:
        """Ошибки плохого пользовательского запроса с 400 кодом"""
        return exception_with_status(status_code=status.HTTP_400_BAD_REQUEST, exc=exc)

    @app.exception_handler(NotFoundException)
    async def handle_not_found_exception(
        request: Request, exc: NotFoundException
    ) -> JSONResponse:
        """Ошибки типа не найдено с 404 кодом"""
        return exception_with_status(status_code=status.HTTP_404_NOT_FOUND, exc=exc)

    @app.exception_handler(AlreadyExistsException)
    async def handle_not_already_exists_exception(
        request: Request, exc: AlreadyExistsException
    ) -> JSONResponse:
        """Ошибки неуникальности с 409 кодом"""
        return exception_with_status(status_code=status.HTTP_409_CONFLICT, exc=exc)

    @app.exception_handler(UnauthorizedException)
    async def handle_unauthorized_exception(
        request: Request, exc: UnauthorizedException
    ) -> JSONResponse:
        """Ошибки для неавторизованного пользователя"""
        return exception_with_status(status_code=status.HTTP_401_UNAUTHORIZED, exc=exc)

    @app.exception_handler(AccessDeniedException)
    async def handle_access_denied_exception(
        request: Request, exc: AccessDeniedException
    ) -> JSONResponse:
        """Ошибки отсутствия прав на действие пользователя"""
        return exception_with_status(status_code=status.HTTP_403_FORBIDDEN, exc=exc)
