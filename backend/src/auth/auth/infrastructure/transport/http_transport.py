import abc

from starlette.requests import Request
from starlette.responses import Response

from backend.src.auth.auth.domain.interfaces.token_transport import ITokenTransport
from backend.src.core.domain.exceptions import DomainException


class HTTPTransport(ITokenTransport, abc.ABC):
    """Абстрактный класс, реализующий передачу токенов через http"""

    request: Request | None
    response: Response | None

    def set_request_response(self, request: Request, response: Response) -> None:
        """Установка объектов запроса и ответа для работы с токенами"""
        self.set_request(request)
        self.set_response(response)

    def set_request(self, request: Request) -> None:
        """Установка запроса для получения из него токенов"""
        self.request = request

    def set_response(self, response: Response) -> None:
        """Установка ответа запроса для установки токенов"""
        self.response = response

    def get_response(self) -> Response:
        """Получение объекта ответа с пробросом ошибки"""
        if not self.response:
            raise DomainException("Не найден объект ответа")
        return self.response

    def get_request(self) -> Request:
        """Получение объекта запроса с пробросом ошибки"""
        if not self.request:
            raise DomainException("Не найден объект запроса")
        return self.request
