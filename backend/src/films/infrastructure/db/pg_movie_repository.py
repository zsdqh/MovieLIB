from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.src.core.domain.exceptions import DomainException, NotFoundException
from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.films.domain.entities.constants import Genre, Profession
from backend.src.films.domain.entities.crud import (
    CreateMovie,
    CreatePerson,
)
from backend.src.films.domain.entities.entities import (
    Country,
    Movie,
    Person,
)
from backend.src.films.domain.interfaces.film_repository import IMovieRepository
from backend.src.films.infrastructure.db.orm import Country as CountryDB
from backend.src.films.infrastructure.db.orm import Genre as GenreDB
from backend.src.films.infrastructure.db.orm import Movie as MovieDB
from backend.src.films.infrastructure.db.orm import Person as PersonDB
from backend.src.films.infrastructure.db.orm import PersonMovie as PersonMovieDB
from backend.src.films.infrastructure.db.orm import Profession as ProfessionDB
from backend.src.films.infrastructure.db.orm import RelatedGroup as RelatedGroupDB
from backend.src.films.infrastructure.db.orm import Type as TypeDB
from backend.src.films.infrastructure.utils.moviedb_to_domain import moviedb_to_domain


class PGMovieRepository(PGRepository, IMovieRepository):
    """Реализация репозитория работы с фильмами в постгрес"""

    async def create_movie(
        self, movie_data: CreateMovie, related_group_id: int | None = None
    ) -> Movie:
        """Создание одного фильма"""
        res = await self.session.execute(
            select(MovieDB)
            .where(MovieDB.id == movie_data.id)
            .options(*MovieDB.get_load_options())
        )
        obj = res.scalar_one_or_none()

        if obj and not obj.is_partial:
            return moviedb_to_domain(obj)

        create_sequels = (not obj) or (obj and obj.is_partial and obj.poster_url == "")

        movie_type = await self.session.get(TypeDB, movie_data.type_number)
        countries = await self._get_or_create_countries(movie_data.countries)
        genres = await self._get_genres(movie_data.genres)

        if related_group_id is None and not obj:
            related_group = await self._create_related_group(movie_data)
        elif not obj or (obj and obj.is_partial and obj.poster_url == ""):
            if not related_group_id:
                raise DomainException(
                    "Частичное создание фильма из серии без передачи related_group_id"
                )
            related_group = await self._get_related_group(related_group_id)
        elif obj:
            related_group = obj.related_group
        else:
            raise DomainException("Проблема с related_group")

        if movie_data.year < related_group.year:
            related_group.name = movie_data.name
            related_group.year = movie_data.year

        await self._get_or_create_partial_persons(movie_data.persons)

        await self._flush_or_exception()

        to_update = {
            **movie_data.model_dump(exclude=CreateMovie.get_excluded_fields()),
            "type": movie_type,
            "related_group": related_group,
            "poster_url": movie_data.poster,
            "backdrop_url": movie_data.backdrop,
            "countries": countries,
            "genres": genres,
        }

        if not obj:
            obj = MovieDB(**to_update)
            self.session.add(obj)
        else:
            for name, val in to_update.items():
                setattr(obj, name, val)

        await self._create_person_movies_for_movie(movie_data.persons, movie_data.id)

        if create_sequels:
            for movie in movie_data.sequels_and_prequels:
                await self.create_movie(movie, related_group.id)

        await self._flush_or_exception()
        await self.session.refresh(obj)

        return moviedb_to_domain(obj)

    async def _get_or_create_countries(
        self, countries: list[Country]
    ) -> list[CountryDB]:
        """Получение списка стран, если страны не существует - создается новая"""
        if not countries:
            return []

        country_names = [c.name for c in countries]
        stmt = select(CountryDB).where(CountryDB.name.in_(country_names))
        res = await self.session.execute(stmt)

        objs = list(res.scalars().all())
        if len(objs) == len(country_names):
            return objs

        names_exist = [obj.name for obj in objs]
        for name in country_names:
            if name not in names_exist:
                created = self._create_country(name)
                objs.append(created)

        return objs

    def _create_country(self, country_name: str) -> CountryDB:
        """Создание одной страны"""
        new_country = CountryDB(name=country_name)
        self.session.add(new_country)
        return new_country

    async def _get_genres(self, genres: list[Genre]) -> list[GenreDB]:
        """Получение жанров"""
        if not genres:
            return []
        stmt = select(GenreDB).where(GenreDB.name.in_(genres))
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def _create_related_group(self, movie_data: CreateMovie) -> RelatedGroupDB:
        """Создание группы фильмов"""
        related_group = RelatedGroupDB(name=movie_data.name, year=movie_data.year)
        self.session.add(related_group)
        return related_group

    async def _get_related_group(self, group_id: int) -> RelatedGroupDB:
        """Получение группы фильмов"""
        stmt = select(RelatedGroupDB).where(RelatedGroupDB.id == group_id)
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj:
            raise NotFoundException("Группа фильмов не найдена")
        return obj

    async def _get_or_create_partial_persons(
        self, persons: Sequence[CreatePerson]
    ) -> list[PersonDB]:
        """Создание или получение частичных данных о пользователе"""
        if not persons:
            return []

        person_ids = [p.id for p in persons]
        stmt = select(PersonDB).where(PersonDB.id.in_(person_ids))
        res = await self.session.execute(stmt)

        objs = list(res.scalars().all())
        if len(objs) == len(persons):
            return objs

        ids_exist = {obj.id for obj in objs}
        for person in persons:
            if person.id not in ids_exist:
                created = await self._get_or_create_partial_person(person)
                objs.append(created)

        return objs

    async def _get_or_create_partial_person(
        self, person_data: CreatePerson
    ) -> PersonDB:
        """Создание или получение данных об одном человеке"""
        stmt = select(PersonDB).where(PersonDB.id == person_data.id)
        res = await self.session.execute(stmt)
        person = res.scalar_one_or_none()
        if person:
            return person

        new_person = PersonDB(
            **person_data.model_dump(exclude=CreatePerson.get_excluded_fields()),
            full_name=person_data.name,
            photo_url=person_data.photo,
        )
        self.session.add(new_person)

        return new_person

    async def _create_person_movies_for_movie(
        self, persons: Sequence[CreatePerson], movie_id: int
    ) -> None:
        """
        Создание связей многие-ко-многим между person и movie с указанием профессии
        """
        to_add = []
        stmt = select(PersonMovieDB).where(PersonMovieDB.movie_id == movie_id)
        res = await self.session.execute(stmt)
        existing = {
            (pm.person_id, pm.movie_id, pm.profession_id) for pm in res.scalars()
        }
        for person in persons:
            if not person.profession:
                continue
            profession = await self._get_profession(person.profession)
            args = (person.id, movie_id, profession.id)
            if args in existing:
                continue
            new_person_movie = PersonMovieDB(
                person_id=person.id, movie_id=movie_id, profession_id=profession.id
            )
            to_add.append(new_person_movie)
        self.session.add_all(to_add)

    async def _get_profession(self, profession_name: str | Profession) -> ProfessionDB:
        """Получение профессии"""
        stmt = select(ProfessionDB).where(ProfessionDB.name == profession_name)
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj:
            raise NotFoundException(f"Профессия {profession_name} не найдена")
        return obj

    async def create_person(self, person_data: CreatePerson) -> Person:
        """Метод создания одного человека из съемочной группы"""
        raise NotImplementedError()

    async def _flush_or_exception(self) -> None:
        """Получение измененных данных из БД с обработкой возникающих ошибок"""
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise DomainException(str(e)) from e
