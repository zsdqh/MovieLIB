from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.rating.base import RatingUseCase
from backend.src.users.domain.dtos import UserRatingSetDTO
from backend.src.users.domain.exceptions import RatingException


class SetRatingUseCase(RatingUseCase):
    """Изменение роли пользователя"""

    async def __call__(
        self, rating_data: UserRatingSetDTO, user_data: TokenUser
    ) -> None:
        rating = rating_data.rating
        if rating > 10 or rating < 1:
            raise RatingException()

        async with self.uow:
            await self.uow.ratings.set_rate(
                user_data.sub, rating_data.movie_id, rating_data.rating
            )
