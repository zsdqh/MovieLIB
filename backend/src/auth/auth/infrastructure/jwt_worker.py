from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.auth.domain.exceptions import InvalidTokenException
from backend.src.auth.auth.domain.interfaces.token_auth import ITokenAuth
from backend.src.auth.auth.infrastructure.jwt_provider import JWTProvider
from backend.src.auth.auth.infrastructure.transport.http_transport import HTTPTransport
from backend.src.core.domain.exceptions import UnauthorizedException


class JWTWorker(ITokenAuth):
    """Класс для основной работы с jwt токенами"""

    token_provider: JWTProvider
    access_transport: HTTPTransport
    refresh_transport: HTTPTransport

    def set_tokens(self, user: TokenUser) -> None:
        access_token = self.token_provider.create_access_token(
            user.model_dump(mode="json")
        )
        refresh_token = self.token_provider.create_refresh_token(
            user.model_dump(mode="json")
        )
        self.access_transport.set_token(access_token)
        self.refresh_transport.set_token(refresh_token)

    def unset_tokens(self) -> None:
        self.access_transport.remove_token()
        self.refresh_transport.remove_token()

    def refresh_tokens(self, user: TokenUser) -> None:

        refresh_token = self.refresh_transport.read_token()
        refresh_data = self.token_provider.read_token(refresh_token)
        if refresh_data.valid_refresh_id != user.valid_refresh_id:
            raise UnauthorizedException("id токена обновления невалиден")
        if not refresh_data:
            raise UnauthorizedException("Чтобы обновить токен сначала авторизуйтесь")

        user.valid_refresh_id += 1

        self.set_tokens(user)

    def get_access_token(self) -> TokenUser:
        try:
            access_token = self.access_transport.read_token()
            access_data = self.token_provider.read_token(access_token)
            if not access_data:
                raise UnauthorizedException()
        except UnauthorizedException as e:
            raise InvalidTokenException("Не найден токен доступа") from e
        return TokenUser.model_validate(access_data)

    def get_refresh_token(self) -> TokenUser:
        refresh_token = self.refresh_transport.read_token()
        refresh_data = self.token_provider.read_token(refresh_token)
        if not refresh_data:
            raise UnauthorizedException("Сначала авторизуйтесь")
        return TokenUser.model_validate(refresh_data)
