from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.rating.base import RatingUseCase


class RatingDestributionUseCase(RatingUseCase):
    """Получение выставленных пользователем оценок фильмам"""

    async def __call__(self, user_data: TokenUser) -> dict[int, int]:
        async with self.uow:
            return await self.uow.ratings.get_user_destribution(user_data.sub)
