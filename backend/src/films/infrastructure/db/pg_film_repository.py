from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.films.domain.entities.crud import CreateMovie, CreatePerson
from backend.src.films.domain.entities.entities import Country, Movie, Person
from backend.src.films.domain.interfaces.film_repository import IFilmRepository


class PGFilmRepository(PGRepository, IFilmRepository):
    """Реализация репозитория работы с фильмами в постгрес"""

    async def get_film_by_id(self, movie_id: int) -> Movie:
        raise NotImplementedError()

    async def get_person_by_id(self, person_id: int) -> Person:
        raise NotImplementedError()

    async def create_movie(self, movie_data: CreateMovie) -> Movie:
        raise NotImplementedError()

    async def create_country(self, country_name: str) -> Country:
        raise NotImplementedError()

    async def create_person(self, person_data: CreatePerson) -> Person:
        raise NotImplementedError()
