import uuid
from datetime import date

import strawberry


@strawberry.input
class CreateHospitalStaffInput:
    staff_number: str
    national_id: str
    full_name: str
    department_id: uuid.UUID
    designation_id: uuid.UUID
    working_site_id: uuid.UUID
    staff_role_id: uuid.UUID | None = None
    phone: str
    date_employed: date
    email: str = ""


@strawberry.input
class UpdateHospitalStaffCapabilitiesInput:
    user_id: uuid.UUID
    capabilities: list[str]


@strawberry.input
class SetRoleCapabilitiesInput:
    role_id: uuid.UUID
    capability_ids: list[uuid.UUID]


@strawberry.input
class UpsertDepartmentHodAssignmentInput:
    department_id: uuid.UUID
    hod_user_id: uuid.UUID
    is_active: bool = True
