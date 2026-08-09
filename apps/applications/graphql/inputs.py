import uuid
from datetime import date

import strawberry


@strawberry.input
class ApplicationDraftInput:
    app_type: str


@strawberry.input
class ApplicationUpdateInput:
    notification_email: str | None = None
    institution_name: str | None = None
    programme_applied: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    programme_duration_value: int | None = None
    programme_duration_unit: str | None = None
    sponsorship_type: str | None = None
    reason_for_study: str | None = None
    attachment_dept: str | None = None
    attachment_start: date | None = None
    attachment_end: date | None = None
    supervisor_requested: str | None = None
    hospital_department_id: uuid.UUID | None = None
    placement_scope: str | None = None
    # Field-attachment specifics
    field_area: str | None = None
    postal_address: str | None = None
    # Student identity (prefilled from profile, editable on the form)
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    faculty: str | None = None
    course: str | None = None
    year_of_study: int | None = None
