import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.src.core.domain.exceptions import (
    BadRequestException,
    DomainException,
    NotFoundException,
)
from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.films.domain.entities.constants import MovieType
from backend.src.films.domain.exceptions import MovieNotFoundException
from backend.src.users.domain.entities import (
    CreateList,
    DeleteList,
    EditList,
    ListMovie,
    MovieInList,
    UserList,
)
from backend.src.users.domain.exceptions import ListNotFoundException
from backend.src.users.domain.interfaces.repository.list_repo import IListRepository
from backend.src.users.infrastructure.db.orm import List as UserListDB
from backend.src.users.infrastructure.db.orm import ListMovie as ListMovieDB


class PGListRepository(PGRepository, IListRepository):
    """Репозиторий для работы с пользовательскими списками фильмов"""

    async def create_list(self, list_data: CreateList) -> UserList:
        obj = UserListDB(**list_data.model_dump())
        obj.list_movies = []
        self.session.add(obj)
        await self.session.flush()
        return self._to_domain(obj)

    async def edit_list(self, update_data: EditList) -> UserList:
        obj = await self._get_user_list(update_data.id, update_data.user_id)

        for name, val in update_data.model_dump(exclude={"id", "user_id"}).items():
            if val is None:
                continue
            setattr(obj, name, val)

        await self.session.flush()
        return self._to_domain(obj)

    async def delete_list(self, delete_data: DeleteList) -> None:
        try:
            obj = await self._get_user_list(delete_data.list_id, delete_data.user_id)
        except NotFoundException:
            return

        await self.session.delete(obj)
        await self.session.flush()

    async def add_movie(self, add_data: ListMovie) -> UserList:
        new_list_movie = ListMovieDB(
            movie_id=add_data.movie_id, list_id=add_data.list_id
        )
        try:
            self.session.add(new_list_movie)
            await self.session.flush()
            await self.session.refresh(new_list_movie)
        except IntegrityError as e:
            orig = str(e.orig).lower()
            if "foreign key constraint" in orig:
                if "movies" in orig:
                    raise MovieNotFoundException(add_data.movie_id) from e
                raise NotFoundException("Список фильмов не найден") from e
            if "duplicate key" in orig:
                await self.session.rollback()
            else:
                raise DomainException(str(e)) from e

        try:
            obj = await self._get_user_list(add_data.list_id, add_data.user_id)
            return self._to_domain(obj)
        except BadRequestException:
            await self.session.rollback()
            raise

    async def remove_movie(self, remove_data: ListMovie) -> UserList:
        obj = await self._get_user_list(remove_data.list_id, remove_data.user_id)

        stmt = select(ListMovieDB).where(
            ListMovieDB.list_id == remove_data.list_id,
            ListMovieDB.movie_id == remove_data.movie_id,
        )
        res = await self.session.execute(stmt)
        to_remove = res.scalar_one_or_none()
        if to_remove:
            try:
                obj.list_movies.remove(to_remove)
                await self.session.delete(to_remove)
                await self.session.flush()
            except ValueError:
                pass

        return self._to_domain(obj)

    async def _get_user_list(
        self, list_id: int, user_id: uuid.UUID, message: str | None = None
    ) -> UserListDB:
        """
        Получение данных о пользовательском списке
        :raises ListNotFoundException: если список не найден
        :raises BadRequestException: если id пользователя не совпадает
         с id владельца списка
        """
        stmt = (
            select(UserListDB)
            .where(UserListDB.id == list_id)
            .options(*UserListDB.get_load_options())
        )
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()

        if not obj:
            raise ListNotFoundException(list_id)

        if obj.user_id != user_id:
            raise BadRequestException(
                message
                if message
                else "Вы можете взаимодействовать только со своими списками"
            )

        return obj

    def _to_domain(self, obj: UserListDB) -> UserList:
        """Преобразование данных о списке из БД в domain объект"""
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
