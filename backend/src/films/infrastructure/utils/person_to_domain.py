from backend.src.films.domain.dtos import MovieFromPersonDTO, PersonDTO
from backend.src.films.domain.entities.constants import Profession
from backend.src.films.domain.entities.entities import MovieFromPerson, Person, Rating


def parse_movies(movies: list[MovieFromPersonDTO]) -> list[MovieFromPerson]:
    """Данные об участии человека в фильме из dto в domain"""
    res = []
    for movie in movies:
        rating = Rating(kp_rating=movie.rating)
        try:
            profession = Profession.from_api(movie.en_profession)
        except KeyError:
            continue
        res.append(
            MovieFromPerson.model_validate(
                {**dict(movie), "rating": rating, "profession": profession}
            )
        )
    return res


def person_to_domain(person_dto: PersonDTO) -> Person:
    """
    Нормализация и маппинг данных о человеке из dto в domain объект
    """
    movies = parse_movies(person_dto.movies)

    return Person.model_validate({**dict(person_dto), "movies": movies})
