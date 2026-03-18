from backend.src.films.domain.entities.constants import Profession
from backend.src.films.domain.entities.entities import MovieFromPerson, Person, Rating
from backend.src.films.infrastructure.db.orm import Person as PersonDB


def persondb_to_domain(person: PersonDB) -> Person:
    """Преобразование данных о человеке из БД в domain сущность"""
    movies = [
        MovieFromPerson(
            **{
                **pm.movie.__dict__,
                "rating": Rating(
                    kp_rating=pm.movie.kp_rating,
                    internal_rating=(
                        pm.movie.get_internal_rating()
                        if pm.movie.get_internal_rating() != 0
                        else None
                    ),
                ),
                "profession": Profession(pm.profession.name),
                "description": pm.description,
            }
        )
        for pm in person.person_movies
    ]
    return Person(
        **person.__dict__, photo=person.photo_url, name=person.full_name, movies=movies
    )
