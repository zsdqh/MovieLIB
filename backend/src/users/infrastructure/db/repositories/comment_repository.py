import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from backend.src.core.domain.exceptions import (
    BadRequestException,
    DomainException,
    NotFoundException,
)
from backend.src.db.infrastructure.pg_repository import PGRepository
from backend.src.films.domain.exceptions import MovieNotFoundException
from backend.src.users.domain.entities import (
    Comment,
    CommentPage,
    CommentReaction,
    CreateComment,
    DeleteComment,
    RemoveReaction,
    ShortUser,
)
from backend.src.users.domain.exceptions import CommentNotFoundException
from backend.src.users.domain.interfaces.repository.comment_repo import (
    ICommentRepository,
)
from backend.src.users.infrastructure.db.orm import Comment as CommentDB
from backend.src.users.infrastructure.db.orm import CommentReaction as CommentReactionDB
from backend.src.users.infrastructure.db.orm import User as UserDB


class PGCommentRepository(PGRepository, ICommentRepository):
    """Postgres реализация репозитория для работы с комментариями"""

    comment_page_size: int = 10

    async def create_comment(self, comment_data: CreateComment) -> Comment:
        new_comment = CommentDB(**comment_data.model_dump())
        self.session.add(new_comment)
        try:
            await self.session.flush()
            await self.session.refresh(new_comment)
        except IntegrityError as e:
            err_msg = str(e.orig).lower()
            if "users" in err_msg:
                raise NotFoundException("Пользователь не найден") from e
            if "movies" in err_msg and comment_data.movie_id:
                raise MovieNotFoundException(comment_data.movie_id) from e
            if "check_comment_target" in err_msg:
                raise DomainException(
                    "Комментарий должен либо быть ответом на другой комментарий, "
                    "либо комментарием к фильму"
                ) from e
            raise DomainException(str(e)) from e

        return self._to_domain(new_comment, False)

    async def delete_comment(
        self, delete_data: DeleteComment, is_admin: bool = False
    ) -> None:
        obj = await self.session.get(CommentDB, delete_data.comment_id)
        if not obj:
            return
        if not is_admin and obj.user_id != delete_data.user_id:
            raise BadRequestException("Вы не можете удалить чужой комментарий")
        await self.session.delete(obj)
        await self.session.flush()

    async def add_reaction(self, reaction_data: CommentReaction) -> Comment:
        comment = await self.session.get(CommentDB, reaction_data.comment_id)

        if not comment:
            raise CommentNotFoundException(reaction_data.comment_id)

        stmt = select(CommentReactionDB).where(
            CommentReactionDB.comment_id == reaction_data.comment_id,
            CommentReactionDB.user_id == reaction_data.user_id,
        )
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()

        if not obj:
            new_reaction = CommentReactionDB(**reaction_data.model_dump())
            if reaction_data.reaction:
                comment.rating += 1
            else:
                comment.rating -= 1
            self.session.add(new_reaction)
        else:
            if obj.reaction == reaction_data.reaction:
                pass
            elif obj.reaction:
                comment.rating -= 2
            else:
                comment.rating += 2
            obj.reaction = reaction_data.reaction

        await self.session.flush()

        return self._to_domain(comment, False)

    async def remove_reaction(self, reaction_data: RemoveReaction) -> Comment:
        comment = await self.session.get(CommentDB, reaction_data.comment_id)
        if not comment:
            raise CommentNotFoundException(reaction_data.comment_id)

        stmt = select(CommentReactionDB).where(
            CommentReactionDB.comment_id == reaction_data.comment_id,
            CommentReactionDB.user_id == reaction_data.user_id,
        )
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()

        if obj:
            if obj.reaction:
                comment.rating -= 1
            else:
                comment.rating += 1
            await self.session.delete(obj)
            await self.session.flush()

        return self._to_domain(comment, False)

    async def get_user_comments(self, user_id: uuid.UUID, page: int = 0) -> CommentPage:
        stmt = (
            select(CommentDB)
            .where(CommentDB.user_id == user_id)
            .order_by(CommentDB.created_at.desc())
            .offset(self.comment_page_size * page)
            .limit(self.comment_page_size + 1)
            # +1 для проверки на то, есть ли следующая страница
        )
        res = await self.session.execute(stmt)
        objs = list(res.scalars().all())
        have_next = False
        comments = []
        for i, comment in enumerate(objs):
            if i == 10:
                have_next = True
                break
            comments.append(self._to_domain(comment, False))

        return CommentPage(
            page=page,
            have_next=have_next,
            comments=comments,
        )

    async def get_movie_comments(self, movie_id: int, page: int = 0) -> CommentPage:
        stmt = (
            select(CommentDB)
            .where(CommentDB.movie_id == movie_id)
            .order_by(CommentDB.created_at.desc())
            .offset(self.comment_page_size * page)
            .limit(self.comment_page_size + 1)
            # +1 для проверки на то, есть ли следующая страница
        )
        res = await self.session.execute(stmt)
        objs = list(res.scalars().all())
        have_next = False
        comments_db = []
        for i, comment in enumerate(objs):
            if i == 10:
                have_next = True
                break
            comments_db.append(await self._get_comment_tree(comment.id))
        return CommentPage(
            page=page,
            have_next=have_next,
            comments=[self._to_domain(comment) for comment in comments_db],
        )

    async def _get_comment_tree(self, root_id: int) -> CommentDB:
        """Рекурсивное получение всех ответов на комментарии"""
        # 1. Построение рекурсивного CTE для комментариев (без пользователей)
        comment_alias = aliased(CommentDB)

        base = select(CommentDB).where(CommentDB.id == root_id)

        cte = base.cte(recursive=True, name="comment_tree")
        cte = cte.union_all(
            select(comment_alias).where(comment_alias.answer_to == cte.c.id)
        )

        stmt = select(cte)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()

        if not rows:
            raise CommentNotFoundException(root_id)
        # 2. Создаём ORM-объекты комментариев
        comments = {}
        for row in rows:
            comment = CommentDB(**row)
            comments[comment.id] = comment

        # 3. Загружаем пользователей для всех комментариев
        user_ids = {c.user_id for c in comments.values()}
        stmt = select(UserDB).where(UserDB.id.in_(user_ids))
        result = await self.session.execute(stmt)
        users = {u.id: u for u in result.scalars().all()}

        # Присваиваем объект user каждому комментарию
        for comment in comments.values():
            comment.user = users[comment.user_id]

        # 4. Строим дерево
        root = None
        for comment in comments.values():
            if comment.answer_to is None:
                root = comment
            else:
                parent = comments.get(comment.answer_to)
                if parent:
                    parent.answers.append(comment)

        for comment in comments.values():
            comment.answers.sort(key=lambda x: x.created_at)

        if root is None:
            root = comments.get(root_id)
            if root is None:
                raise CommentNotFoundException(root_id)

        return root

    def _to_domain(self, obj: CommentDB, with_answers: bool = True) -> Comment:
        """
        Преобразование объекта из БД в domain объект
        если выставлен флаг with_answers - рекурсивно загружает все ответы
        """
        if with_answers:
            answers = [self._to_domain(comment) for comment in obj.answers]
        else:
            answers = []
        user = ShortUser.model_validate(obj.user.__dict__)
        return Comment.model_validate(
            {**obj.__dict__, "answers": answers, "user": user}
        )
