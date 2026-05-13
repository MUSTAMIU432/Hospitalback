import strawberry


@strawberry.type
class StatusCount:
    status: str
    count: int


@strawberry.type
class DashboardDigest:
    applications_total: int
    applications_by_status: list[StatusCount]
    hospital_staff_total: int
    students_total: int
    users_total: int
    unread_notifications: int
    recent_import_batches: int
