import abc


class ITokenTransport(abc.ABC):
    """Способ передачи токена пользователю"""

    @abc.abstractmethod
    def set_token(self, token: str) -> None:
        """Установка токена в ответ"""

    @abc.abstractmethod
    def remove_token(self) -> None:
        """Удаление токена из ответа"""

    @abc.abstractmethod
    def read_token(self) -> str:
        """Чтение токена из запроса"""
