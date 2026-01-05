from fastapi import FastAPI
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.src.auth.auth.presentation.auth_middleware import fetch_url_path
from backend.src.core.domain.exceptions import (
    AccessDeniedException,
)
from backend.src.core.exception_handlers import exception_with_status


class UserActiveMiddleware(BaseHTTPMiddleware):
    """Проверка на то, активен ли аккаунт или нет"""

    def __init__(self, app: FastAPI, public: list[str] | None = None):
        super().__init__(app)
        if not public:
            public = [
                "/send_confirmation",
                "/confirm_email",
                "/me",
                "/refresh",
                "/logout",
            ]
        self.public = public

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Проверка статуса при запросе на непубличный эндпоинт"""
        try:
            user_data = request.state.user
            url = fetch_url_path(request)

            if url not in self.public:
                problems = []
                if not user_data.is_activated:
                    problems.append("email address is not confirmed")
                if user_data.is_blocked:
                    problems.append("account is blocked by admin")
                if problems:
                    return exception_with_status(
                        status_code=status.HTTP_403_FORBIDDEN,
                        exc=AccessDeniedException(f"Your {", ".join(problems)}"),
                    )
        except AttributeError:
            # Вызовется, если не удастся получить данные о пользователе из запроса
            # Если AuthenticationMiddleware не передал данные о пользователе,
            # значит эндпоинт, к которому обращается пользователь,
            # публичный и для него не нужна проверка
            # или запрос идет от внутреннего сервиса
            pass
        response = await call_next(request)
        return response
