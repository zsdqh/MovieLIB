from typing import Literal

from backend.src.auth.auth.infrastructure.transport.http_transport import HTTPTransport
from backend.src.core.domain.exceptions import UnauthorizedException


class CookieTransport(HTTPTransport):
    """Передача токена внутри cookie"""

    def __init__(
        self,
        cookie_name: str,
        cookie_max_age: int | None = None,
        cookie_path: str = "/",
        cookie_domain: str | None = None,
        cookie_secure: bool = False,
        cookie_httponly: bool = True,
        cookie_samesite: Literal["lax", "strict", "none"] = "lax",
    ):
        """Настройки cookie"""
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite

    def set_token(self, token: str) -> None:
        """Добавление coookie в response"""
        self.get_response().set_cookie(
            key=self.cookie_name,
            value=token,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )

    def remove_token(self) -> None:
        """Удаление cookie из ответа"""
        self.get_response().delete_cookie(
            key=self.cookie_name,
            path=self.cookie_path,
            domain=self.cookie_domain,
        )

    def read_token(self) -> str:
        """Считать токен из cookie"""
        cookie = self.get_request().cookies.get(self.cookie_name)
        if not cookie:
            raise UnauthorizedException("Токен не найден в cookie")
        return cookie
