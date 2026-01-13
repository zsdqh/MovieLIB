from backend.src.auth.auth.domain.exceptions import InvalidTokenException
from backend.src.auth.auth.infrastructure.transport.http_transport import HTTPTransport
from backend.src.core.domain.exceptions import UnauthorizedException


class HeaderTransport(HTTPTransport):
    """Отправка токена через заголовки"""

    def __init__(
        self,
        header_name: str,
        token_type_prefix: str | None = None,
    ) -> None:
        """Ключа и префикс заголовка"""
        self.header_name = header_name
        self.token_type_prefix = token_type_prefix

    def set_token(self, token: str) -> None:
        """Установить токен в заголовок ответа"""
        if self.token_type_prefix:
            token_value = f"{self.token_type_prefix} {token}"
        else:
            token_value = token
        self.get_response().headers[self.header_name] = token_value

    def remove_token(self) -> None:
        """Удалить токен из заголовков ответа"""
        self.get_response().headers[self.header_name] = ""

    def read_token(self) -> str:
        """Считать токен из заголовка"""
        header = self.get_request().headers.get(self.header_name)
        if not header:
            raise UnauthorizedException("Токен не найден в заголовках")
        try:
            return header.split(" ")[1]
        except IndexError as e:
            raise InvalidTokenException(
                "Неправильный формат заголовка авторизации"
            ) from e
