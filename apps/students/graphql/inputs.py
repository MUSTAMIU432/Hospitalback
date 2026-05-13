import uuid

import strawberry


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
