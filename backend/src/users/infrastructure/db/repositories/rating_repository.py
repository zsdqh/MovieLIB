import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.films.domain.exceptions import MovieNotFoundException
from backend.src.users.domain.interfaces.repository.rating_repo import IRatingRepository
from backend.src.users.infrastructure.db.orm import UserRating


class PGRatingRepository(PGRepository, IRatingRepository):
    """Репозиторий для работы с внутренними оценками фильмов"""

    async def set_rate(self, user_id: uuid.UUID, movie_id: int, rating: int) -> None:
        obj = await self._get_user_rating(user_id, movie_id)
        try:
            if obj:
                obj.movie.votes_sum += rating - obj.rating
                obj.rating = rating
            else:
                obj = UserRating(user_id=user_id, movie_id=movie_id, rating=rating)
                self.session.add(obj)

                await self.session.flush()
                await self.session.refresh(obj)

                obj.movie.votes_count += 1
                obj.movie.votes_sum += rating
                await self.session.flush()
        except IntegrityError as e:
            raise MovieNotFoundException(movie_id) from e

    async def remove_rate(self, user_id: uuid.UUID, movie_id: int) -> None:
        obj = await self._get_user_rating(user_id, movie_id)

        if not obj:
            return

        obj.movie.votes_sum -= obj.rating
        obj.movie.votes_count -= 1

        await self.session.delete(obj)
        await self.session.flush()

    async def _get_user_rating(
        self, user_id: uuid.UUID, movie_id: int
    ) -> UserRating | None:
        """Получение UserRating по данным о пользователе и фильме"""
        stmt = select(UserRating).where(
            UserRating.user_id == user_id, UserRating.movie_id == movie_id
        )
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        return obj
