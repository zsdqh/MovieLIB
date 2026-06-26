from backend.src.films.domain.entities.constants import Genre, MovieType
from backend.src.films.infrastructure.db.orm import Movie
from backend.src.users.domain.entities import MovieInList, UserList
from backend.src.users.infrastructure.db.orm import List


def _extract_movie_genres(movie: Movie) -> list[Genre]:
    """Преобразование жанров ORM фильма в доменный список Genre."""
    out: list[Genre] = []
    for genre_obj in getattr(movie, "genres", []) or []:
        name = getattr(genre_obj, "name", None)
        if not name:
            continue
        try:
            out.append(Genre(name))
        except ValueError:
            continue
    return out


def listbd_to_domain(obj: List) -> UserList:
    """Функция преобразования списка из базы данных в domain объект"""
    movies = [
        MovieInList(
            type=MovieType(lm.movie.type.id),
            id=lm.movie_id,
            poster=lm.movie.poster_url,
            name=lm.movie.name,
            created_at=lm.created_at,
            genres=_extract_movie_genres(lm.movie),
        )
        for lm in obj.list_movies
    ]
    return UserList.model_validate({**obj.__dict__, "movies": movies})
