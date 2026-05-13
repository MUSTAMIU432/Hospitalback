import strawberry
from strawberry.types import Info

from apps.reports.graphql.types import DashboardDigest, StatusCount
from apps.reports.services.digest import dashboard_digest_for_user
from apps.users.graphql.auth import require_auth


@strawberry.type
class ReportsQuery:
    @strawberry.field
    def dashboard_digest(self, info: Info) -> DashboardDigest:
        user = require_auth(info)
        raw = dashboard_digest_for_user(user)
        pairs = [
            StatusCount(status=row["status"], count=row["c"])
            for row in raw["applications_by_status"]
        ]
        return DashboardDigest(
            applications_total=raw["applications_total"],
            applications_by_status=pairs,
            hospital_staff_total=raw["hospital_staff_total"],
            students_total=raw["students_total"],
            users_total=raw["users_total"],
            unread_notifications=raw["unread_notifications"],
            recent_import_batches=raw["recent_import_batches"],
        )
