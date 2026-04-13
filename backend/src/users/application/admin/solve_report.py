from backend.src.auth.auth.application.check_permissions import check_admin_only
from backend.src.auth.auth.domain.entities import TokenUser
from backend.src.users.application.admin.base import AdminUseCase
from backend.src.users.domain.entities import Report


class SolveReportUseCase(AdminUseCase):
    """Отметка жалобы выполненной"""

    async def __call__(self, report_id: int, user_data: TokenUser) -> Report:
        check_admin_only(user_data)
        async with self.uow:
            return await self.uow.admin_work.solve_report(report_id)
