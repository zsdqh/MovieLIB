from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.base import UserUseCase
from backend.src.users.domain.dtos import CreateReportDTO
from backend.src.users.domain.entities import CreateReport, Report


class ReportUserUseCase(UserUseCase):
    """Создание жалобы на пользователя"""

    async def __call__(
        self, create_data: CreateReportDTO, user_data: TokenUser
    ) -> Report:
        async with self.uow:
            return await self.uow.users.report_user(
                CreateReport(**create_data.model_dump(), created_by_id=user_data.sub)
            )
