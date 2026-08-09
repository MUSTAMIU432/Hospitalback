import uuid

import strawberry


@strawberry.input
class CompleteStudentProfileInput:
    """What a self-registered student fills in for themselves.

    Mirrors CreateStudentInput minus the fields only staff may set —
    `supervisor_user_id`, `hospital_department_id` and `dashboard_notes` are
    assignments and staff notes, not self-declarations, so they are absent here
    rather than merely ignored.
    """

    registration_no: str
    full_name: str
    programme: str
    faculty: str
    year_of_study: int
    phone: str
    dob: str
    university: str = "Zanzibar University"
    gender: str = "unspecified"
    level_of_study: str = ""
    middle_name: str = ""
    # Correspondence address for placements. Defaults to the account email the
    # student registered with when left blank, so the common case needs nothing.
    contact_email: str = ""
    faculty_entity_id: uuid.UUID | None = None
    department_entity_id: uuid.UUID | None = None


@strawberry.input
class CreateStudentInput:
    registration_no: str
    full_name: str
    programme: str
    faculty: str
    year_of_study: int
    phone: str
    dob: str
    university: str = "Zanzibar University"
    supervisor_user_id: uuid.UUID | None = None
    email: str = ""
    contact_email: str = ""
    gender: str = "unspecified"
    hospital_department_id: uuid.UUID | None = None
    dashboard_notes: str = ""
    faculty_entity_id: uuid.UUID | None = None
    department_entity_id: uuid.UUID | None = None
    level_of_study: str = ""
