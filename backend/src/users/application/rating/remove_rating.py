from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.rating.base import RatingUseCase


class RemoveRatingUseCase(RatingUseCase):
    """Удаление оценки фильма пользователеим"""

    async def __call__(self, movie_id: int, user_data: TokenUser) -> None:
        async with self.uow:
            await self.uow.ratings.remove_rate(user_data.sub, movie_id)
