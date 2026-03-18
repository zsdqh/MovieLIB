from backend.src.films.domain.entities.constants import Genre, MovieType, Profession
from backend.src.films.domain.entities.entities import (
    Country,
    Movie,
    Rating,
    ShortMovie,
    ShortPerson,
)
from backend.src.films.infrastructure.db.orm import Movie as MovieDB


def moviedb_to_domain(movie: MovieDB) -> Movie:
    """Преобразование объекта из БД в domain объект"""
    internal_rating = movie.get_internal_rating()
    genres = [Genre(genre.name) for genre in movie.genres]
    countries = [Country(name=country.name) for country in movie.countries]
    persons = [
        ShortPerson(
            profession=Profession(person_movie.profession.name),
            **person_movie.person.__dict__,
            photo=person_movie.person.photo_url,
            name=person_movie.person.full_name
        )
        for person_movie in movie.person_movies
    ]
    sequels_and_prequels = []
    if movie.related_group:
        sequels_and_prequels = [
            ShortMovie(
                **{
                    **sequel.__dict__,
                    "poster": sequel.poster_url,
                    "type": MovieType(sequel.type_id),
                }
            )
            for sequel in movie.related_group.movies
            if sequel.id != movie.id
        ]
    return Movie(
        **{
            **movie.__dict__,
            "type": MovieType(movie.type_id),
            "rating": Rating(
                kp_rating=movie.kp_rating,
                internal_rating=internal_rating if internal_rating != 0 else None,
            ),
            "poster": movie.poster_url,
            "backdrop": movie.backdrop_url,
            "genres": genres,
            "countries": countries,
            "persons": persons,
            "sequels_and_prequels": sequels_and_prequels,
        }
    )
