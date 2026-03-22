from backend.src.films.domain.entities.constants import MovieType
from backend.src.users.domain.entities import MovieInList, UserList
from backend.src.users.infrastructure.db.orm import List


def listbd_to_domain(obj: List) -> UserList:
    """Функция преобразования списка из базы данных в domain объект"""
    movies = [
        MovieInList(
            type=MovieType(lm.movie.type.id),
            id=lm.movie_id,
            poster=lm.movie.poster_url,
            name=lm.movie.name,
            created_at=lm.created_at,
        )
        for lm in obj.list_movies
    ]
    return UserList.model_validate({**obj.__dict__, "movies": movies})
