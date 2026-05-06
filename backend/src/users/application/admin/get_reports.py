from datetime import date

from backend.src.auth.auth.application.check_permissions import check_admin_only
from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.admin.base import AdminUseCase
from backend.src.users.domain.entities import Report


class GetReportsUseCase(AdminUseCase):
    """Получение жалоб за определенный период"""

    async def __call__(
        self, start_from: date | None, user_data: TokenUser
    ) -> list[Report]:
        check_admin_only(user_data)
        async with self.uow:
            return await self.uow.admin_work.get_reports(start_from)
