import uuid
from datetime import date

import strawberry


@strawberry.input
class ApplicationDraftInput:
    app_type: str


@strawberry.input
class ApplicationUpdateInput:
    institution_name: str | None = None
    programme_applied: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    sponsorship_type: str | None = None
    reason_for_study: str | None = None
    attachment_dept: str | None = None
    attachment_start: date | None = None
    attachment_end: date | None = None
    supervisor_requested: str | None = None
    hospital_department_id: uuid.UUID | None = None
    placement_scope: str | None = None
