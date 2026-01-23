from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.core.domain.exceptions import AccessDeniedException


def check_admin_only(user_data: TokenUser) -> None:
    """Проверка наличия необходимых прав у пользователя для выполнения действия"""
    if not user_data.is_admin:
        raise AccessDeniedException("У вас нет прав на это действие")
