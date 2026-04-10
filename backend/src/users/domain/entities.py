"""Сущности с корректными данными для работы функций"""

import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field

from backend.src.films.domain.entities.constants import MovieType


class UserBase(BaseModel):
    """Стандартные поля моделей пользователя"""

    email: str
    username: str = Field(min_length=3)


class User(UserBase):
    """Модель для передачи объекта из БД между функциями"""

    id: uuid.UUID
    hashed_password: str
    created_at: datetime.datetime
    valid_refresh_id: int
    avatar_url: str | None = None
    is_activated: bool
    is_admin: bool
    user_lists: list["UserList"] = []
    active_blockings: list["Blocking"] = []


class UserRegister(UserBase):
    """Данные для регистрации пользователя"""

    hashed_password: str


class UserUpdate(BaseModel):
    """
    Изменяемые данные пользователя
    None - поле не будет изменено
    """

    id: uuid.UUID
    email: EmailStr | None = None
    username: str | None = None
    hashed_password: str | None = None
    valid_refresh_id: int | None = None
    is_activated: bool | None = None
    is_admin: bool | None = None
    avatar_url: str | None = None


class UserPublic(UserBase):
    """Данные о пользователе, выводимые в ответах"""

    id: uuid.UUID
    created_at: datetime.datetime
    avatar_url: str | None = None
    is_activated: bool
    is_blocked: bool = False
    is_admin: bool
    user_lists: list["UserList"] = []


class MovieInList(BaseModel):
    """Отображаемые данные о фильме внутри пользовательского списка"""

    id: int
    poster: str
    name: str
    created_at: datetime.datetime
    type: MovieType


class UserList(BaseModel):
    """Данные о пользовательском списке"""

    id: int
    name: str
    is_public: bool
    movies: list[MovieInList]


class CreateList(BaseModel):
    """Данные для создания пользовательского списка"""

    user_id: uuid.UUID
    name: str
    is_public: bool = False


class EditList(BaseModel):
    """
    Данные для изменения пользовательского списка
    None - значение не изменяется
    """

    id: int
    user_id: uuid.UUID
    name: str | None = None
    is_public: bool | None = None


class ListMovie(BaseModel):
    """Данные о связи между фильмом и пользовательской группой"""

    user_id: uuid.UUID
    list_id: int
    movie_id: int


class DeleteList(BaseModel):
    """Данные для удаления пользовательского списка"""

    user_id: uuid.UUID
    list_id: int


class ShortUser(BaseModel):
    """Данные, отображаемые о пользователе в комментарии"""

    id: uuid.UUID
    username: str
    avatar_url: str | None


class Comment(BaseModel):
    """Данные о комментарии"""

    id: int
    text: str
    answer_to: int | None = None
    user: ShortUser
    created_at: datetime.datetime
    rating: int = 0
    movie_id: int | None = None
    answers: list["Comment"] = []


class CreateComment(BaseModel):
    """Данные для создания комментария"""

    text: str
    answer_to: int | None = None
    user_id: uuid.UUID
    movie_id: int | None = None


class CommentPersonIds(BaseModel):
    """Базовый класс с id комментария и пользователя"""

    comment_id: int
    user_id: uuid.UUID


class DeleteComment(CommentPersonIds):
    """Данные для удаления комментария"""


class CommentReaction(CommentPersonIds):
    """Данные о реакции пользователя на комментарий"""

    reaction: bool


class RemoveReaction(CommentPersonIds):
    """Данные для удаления реакции на комментарий"""


class CommentPage(BaseModel):
    """Страница комментариев для пагинации"""

    comments: list[Comment]
    page: int
    have_next: bool


class Report(BaseModel):
    """Данные о жалобе"""

    id: int
    reason: str
    solved: bool
    created_at: datetime.datetime
    created_by: ShortUser
    user: ShortUser
    comment: Comment | None = None


class Blocking(BaseModel):
    """Общие данные о блокировке"""

    id: int
    reason: str
    ends_at: datetime.datetime | None


class BlockingWithUser(Blocking):
    """Данные о блокировке, включая пользователя"""

    user: ShortUser


class CreateBlocking(Blocking):
    """Данные для создания блокировки"""

    user_id: uuid.UUID


class CreateReport(BaseModel):
    """Данные для создания жалобы"""

    reason: str
    created_by: uuid.UUID
    user_id: uuid.UUID
    comment_id: int | None = None
