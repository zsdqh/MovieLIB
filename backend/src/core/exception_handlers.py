from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response

from backend.src.core.container import Container
from backend.src.core.domain.exceptions import (
    AccessDeniedException,
    AlreadyExistsException,
    BadRequestException,
    DomainException,
    NotFoundException,
    UnauthorizedException,
)
from backend.src.films.presentation.api import templates_annotation


@inject
def exception_with_status(
    status_code: int,
    exc: DomainException,
    request: Request,
    templates: templates_annotation = Provide[Container.templates],
) -> JSONResponse | HTMLResponse:
    """Превращение Domain ошибки в отправляемый ответ"""
    context = {"detail": exc.detail}
    if "json" in request.headers.get("accept", "") or not templates:
        return JSONResponse(status_code=status_code, content=context)
    return templates.TemplateResponse(
        request,
        name="error.html",
        status_code=status_code,
        context={**context, "status_code": status_code},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Создание обработчиков ошибок для их корректного вывода пользователю"""

    @app.exception_handler(DomainException)
    async def handle_server_exception(
        request: Request, exc: DomainException
    ) -> Response:
        """Внутренние ошибки сервера(неизвестные) с 500 кодом"""
        return exception_with_status(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, exc=exc, request=request
        )

    @app.exception_handler(BadRequestException)
    async def handle_bad_request_exception(
        request: Request, exc: BadRequestException
    ) -> Response:
        """Ошибки плохого пользовательского запроса с 400 кодом"""
        return exception_with_status(
            status_code=status.HTTP_400_BAD_REQUEST, exc=exc, request=request
        )

    @app.exception_handler(NotFoundException)
    async def handle_not_found_exception(
        request: Request, exc: NotFoundException
    ) -> Response:
        """Ошибки типа не найдено с 404 кодом"""
        return exception_with_status(
            status_code=status.HTTP_404_NOT_FOUND, exc=exc, request=request
        )

    @app.exception_handler(AlreadyExistsException)
    async def handle_not_already_exists_exception(
        request: Request, exc: AlreadyExistsException
    ) -> Response:
        """Ошибки неуникальности с 409 кодом"""
        return exception_with_status(
            status_code=status.HTTP_409_CONFLICT, exc=exc, request=request
        )

    @app.exception_handler(UnauthorizedException)
    async def handle_unauthorized_exception(
        request: Request, exc: UnauthorizedException
    ) -> Response:
        """Ошибки для неавторизованного пользователя"""
        return exception_with_status(
            status_code=status.HTTP_401_UNAUTHORIZED, exc=exc, request=request
        )

    @app.exception_handler(AccessDeniedException)
    async def handle_access_denied_exception(
        request: Request, exc: AccessDeniedException
    ) -> Response:
        """Ошибки отсутствия прав на действие пользователя"""
        return exception_with_status(
            status_code=status.HTTP_403_FORBIDDEN, exc=exc, request=request
        )

    @app.exception_handler(404)
    async def custom_404_handler(request: Request, __: Exception) -> Response:
        return exception_with_status(
            status_code=status.HTTP_404_NOT_FOUND,
            exc=NotFoundException("Страница не найдена"),
            request=request,
        )
