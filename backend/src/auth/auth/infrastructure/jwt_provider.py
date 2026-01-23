from datetime import datetime, timedelta
from typing import Any

import jwt
from jwt import DecodeError, ExpiredSignatureError

from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.auth.auth.domain.interfaces.token_provider import ITokenProvider
from backend.src.core.config import JWTSettings
from backend.src.core.domain.exceptions import UnauthorizedException


class JWTProvider(ITokenProvider):
    """Класс для генерации и считывания jwt токенов"""

    def __init__(self, config: JWTSettings):
        """
        Настройки для работы с jwt, такие, как секретный ключ,
        время жизни токенов и метод шифрования
        """
        self.config = config

    def create_access_token(self, data: dict[str, Any]) -> str:
        """Создание access токена"""
        return self._create_token(data, self.config.access_ttl)

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        """Создание refresh токена"""
        return self._create_token(data, self.config.refresh_ttl)

    def _create_token(self, data: dict[str, Any], ttl: int) -> str:
        """Создание jwt с payload из data и временем жизни ttl секунд"""
        payload = data.copy()
        payload["exp"] = datetime.now() + timedelta(seconds=ttl)
        return jwt.encode(payload, self.config.secret_key, self.config.algorithm)

    def read_token(self, token: str) -> TokenUser:
        """Получение данных о пользователе из токена"""
        data = self._decode(
            token,
            options={
                "verify_signature": True,
                "verify_exp": True,
            },
        )
        return TokenUser.model_validate(data)

    def _decode(self, token: str, options: dict[str, bool]) -> Any:
        """Получение данных из jwt"""
        try:
            data = jwt.decode(
                token,
                self.config.secret_key,
                self.config.algorithm,
                options=options,
            )
            return data
        except ExpiredSignatureError as e:
            raise UnauthorizedException("Срок действия токена истек") from e
        except (DecodeError, ValueError, IndexError) as e:
            raise UnauthorizedException(
                "Токен невалиден, попробуйте перейти на /refresh"
            ) from e
