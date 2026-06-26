import abc

from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.auth.domain.interfaces.token_provider import ITokenProvider
from backend.src.auth.auth.domain.interfaces.token_transport import ITokenTransport


class ITokenAuth(abc.ABC):
    """Интерфейс класса работника с токенами"""

    def __init__(
        self,
        token_provider: ITokenProvider,
        access_transport: ITokenTransport,
        refresh_transport: ITokenTransport,
    ):
        """Создание с генератором токенов"""
        self.token_provider = token_provider
        self.access_transport = access_transport
        self.refresh_transport = refresh_transport

    @abc.abstractmethod
    def set_tokens(self, user: TokenUser) -> None:
        """Устанавливаем оба токена в ответ"""

    @abc.abstractmethod
    def unset_tokens(self) -> None:
        """Убираем токены из ответа (пользователь разлогинился)"""

    @abc.abstractmethod
    def refresh_tokens(self, user: TokenUser) -> None:
        """Выдаем новую пару токенов"""

    @abc.abstractmethod
    def get_access_token(self) -> TokenUser:
        """Получение access токена"""

    @abc.abstractmethod
    def get_refresh_token(self) -> TokenUser:
        """Получение refresh токена"""
