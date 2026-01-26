from backend.src.films.domain.dtos import MovieDTO, PersonDTO
from backend.src.films.domain.entities.filters import FilmParams, RandomParams
from backend.src.films.domain.interfaces.get_film_repository import IGetFilmRepository
from backend.src.users.infrastructure.db.repositories.pg_repository import PGRepository


class PGGetFilmRepository(PGRepository, IGetFilmRepository):
    """Реализация репозитория для получения фильмов из БД"""

    async def get_film_by_id(self, movie_id: int) -> MovieDTO | None:
        raise NotImplementedError()

    async def get_films_by_id(self, movie_ids: list[int]) -> list[MovieDTO]:
        raise NotImplementedError()

    async def get_films_by_name(self, film_name: str) -> list[MovieDTO]:
        raise NotImplementedError()

    async def get_films_with_params(self, params: FilmParams) -> list[MovieDTO]:
        raise NotImplementedError()

    async def get_random_film(self, params: RandomParams) -> MovieDTO | None:
        raise NotImplementedError()

    async def get_person_by_id(self, person_id: int) -> PersonDTO | None:
        raise NotImplementedError()

    async def get_persons_by_id(self, person_ids: list[int]) -> list[PersonDTO]:
        raise NotImplementedError()
