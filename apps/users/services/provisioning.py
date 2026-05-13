from __future__ import annotations

import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import transaction

from apps.employees.models import HospitalStaff, StaffRole
from apps.hospital_directory.models import Department, Designation, WorkingSite
from apps.students.models import StudentProfile, UniversityDepartment, UniversityFaculty
from apps.users.services.student_credentials import student_default_password_from_full_name
from core.constants import Gender, UserModule, UserRole

User = get_user_model()


def default_staff_role() -> StaffRole:
    role, _ = StaffRole.objects.get_or_create(
        code="staff",
        defaults={"name": "Staff", "description": "General staff role", "is_active": True, "sort_order": 0},
    )
    return role


def _directory_fks(
    department_id: uuid.UUID,
    designation_id: uuid.UUID,
    working_site_id: uuid.UUID,
) -> tuple[Department, Designation, WorkingSite]:
    try:
        dept = Department.objects.get(pk=department_id)
        des = Designation.objects.get(pk=designation_id)
        site = WorkingSite.objects.get(pk=working_site_id)
    except ObjectDoesNotExist as exc:
        raise ValidationError(
            "Invalid department, designation, or working site id."
        ) from exc
    return dept, des, site


@transaction.atomic
def create_hospital_staff_user(
    *,
    acting_user,
    staff_number: str,
    national_id: str,
    full_name: str,
    department_id: uuid.UUID,
    designation_id: uuid.UUID,
    working_site_id: uuid.UUID,
    staff_role_id: uuid.UUID | None,
    phone: str,
    date_employed,
    email: str = "",
) -> tuple[Any, HospitalStaff]:
    role = getattr(acting_user, "role", None)
    if role != UserRole.HOSPITAL_ADMIN:
        raise PermissionDenied("Not allowed to create hospital staff users.")
    if User.objects.filter(username=staff_number).exists():
        raise ValidationError("A user with this staff number already exists.")
    dept, des, site = _directory_fks(department_id, designation_id, working_site_id)
    if staff_role_id:
        try:
            role_row = StaffRole.objects.get(pk=staff_role_id, is_active=True)
        except StaffRole.DoesNotExist as exc:
            raise ValidationError("Select an active staff role.") from exc
    else:
        role_row = default_staff_role()
    default_pw = student_default_password_from_full_name(full_name)
    if not default_pw:
        raise ValidationError(
            "Full name must include at least one given name (used as the initial sign-in password)."
        )
    user = User.objects.create_user(
        username=staff_number,
        password=default_pw,
        email=email or "",
        first_name=default_pw[:150],
        role=UserRole.HOSPITAL_STAFF,
        module=UserModule.FURTHER_STUDIES,
    )
    user.is_first_login = True
    user.save(update_fields=["is_first_login"])
    profile = HospitalStaff(
        user=user,
        staff_number=staff_number,
        full_name=full_name,
        department=dept,
        designation=des,
        working_site=site,
        phone=phone,
        national_id=national_id,
        date_employed=date_employed,
        staff_role=role_row,
        capabilities=[],
    )
    profile.full_clean()
    profile.save()
    return user, profile


@transaction.atomic
def create_student_user(
    *,
    acting_user,
    registration_no: str,
    full_name: str,
    programme: str,
    faculty: str,
    year_of_study: int,
    phone: str,
    dob: str,
    university: str = "Zanzibar University",
    supervisor_user=None,
    email: str = "",
    contact_email: str = "",
    gender: str = Gender.UNSPECIFIED,
    hospital_department_id: uuid.UUID | None = None,
    dashboard_notes: str = "",
    faculty_entity_id: uuid.UUID | None = None,
    department_entity_id: uuid.UUID | None = None,
    level_of_study: str = "",
) -> tuple[Any, StudentProfile]:
    from core.constants import STUDENT_MANAGER_ROLES
    role = getattr(acting_user, "role", None)
    if role not in STUDENT_MANAGER_ROLES:
        raise PermissionDenied("Not allowed to create students.")
    if User.objects.filter(username=registration_no).exists():
        raise ValidationError("A user with this registration number already exists.")
    allowed_gender = {c.value for c in Gender}
    if gender not in allowed_gender:
        raise ValidationError("Invalid gender value.")
    hosp_dept = None
    if hospital_department_id is not None:
        try:
            hosp_dept = Department.objects.get(pk=hospital_department_id)
        except Department.DoesNotExist as exc:
            raise ValidationError("Hospital department not found.") from exc
    fac_obj: UniversityFaculty | None = None
    dep_obj: UniversityDepartment | None = None
    faculty_display = faculty.strip()
    if faculty_entity_id is not None:
        try:
            fac_obj = UniversityFaculty.objects.get(pk=faculty_entity_id)
        except UniversityFaculty.DoesNotExist as exc:
            raise ValidationError("University faculty not found.") from exc
        faculty_display = fac_obj.name
    if department_entity_id is not None:
        try:
            dep_obj = UniversityDepartment.objects.select_related("faculty").get(
                pk=department_entity_id
            )
        except UniversityDepartment.DoesNotExist as exc:
            raise ValidationError("University department not found.") from exc
        if fac_obj is not None and dep_obj.faculty_id != fac_obj.id:
            raise ValidationError("Department does not belong to the selected faculty.")
        fac_obj = fac_obj or dep_obj.faculty
        faculty_display = dep_obj.faculty.name
    default_pw = student_default_password_from_full_name(full_name)
    if not default_pw:
        raise ValidationError(
            "Full name must include at least one given name (used as the initial sign-in password)."
        )
    user = User.objects.create_user(
        username=registration_no,
        password=default_pw,
        email=email or "",
        first_name=default_pw[:150],
        role=UserRole.STUDENT,
        module=UserModule.ATTACHMENT,
    )
    user.is_first_login = True
    user.save(update_fields=["is_first_login"])
    profile = StudentProfile.objects.create(
        user=user,
        registration_no=registration_no,
        full_name=full_name,
        programme=programme,
        faculty=faculty_display or faculty,
        faculty_entity=fac_obj,
        department_entity=dep_obj,
        level_of_study=(level_of_study or "").strip()[:30],
        year_of_study=year_of_study,
        phone=phone,
        contact_email=contact_email or "",
        gender=gender,
        dob=dob,
        university=university,
        hospital_department=hosp_dept,
        dashboard_notes=dashboard_notes or "",
        supervisor=supervisor_user,
    )
    return user, profile


@transaction.atomic
def create_tenant_admin_user(
    *,
    acting_user,
    username: str,
    password: str | None = None,
    role: str,
    email: str = "",
    first_name: str = "",
) -> Any:
    """System admin only: provision hospital or university tenant administrators."""
    _ = password  # unused; initial password is always the first given name token (same rule as staff/students).
    if getattr(acting_user, "role", None) != UserRole.SYSADMIN:
        raise PermissionDenied("Only system administrators may create tenant administrators.")
    if role not in (UserRole.HOSPITAL_ADMIN, UserRole.UNIV_ADMIN):
        raise ValidationError("Role must be hospital admin or university admin.")
    uname = username.strip()
    if not uname:
        raise ValidationError("Username is required.")
    if User.objects.filter(username=uname).exists():
        raise ValidationError("A user with this username already exists.")
    display = (first_name or uname).strip()[:150]
    initial_pw = student_default_password_from_full_name(display)
    if not initial_pw:
        raise ValidationError(
            "Display name must include at least one given name (used as the initial sign-in password). "
            "You can enter a full name in Display name, or a username whose first word is usable."
        )
    user = User.objects.create_user(
        username=uname,
        password=initial_pw,
        email=(email or "").strip(),
        first_name=display[:150],
        role=role,
        module=UserModule.ADMIN,
    )
    user.is_first_login = True
    user.save(update_fields=["is_first_login"])
    return user


def resolve_hod_user(hod_id: uuid.UUID | None):
    if hod_id is None:
        return None
    try:
        u = User.objects.get(pk=hod_id)
    except User.DoesNotExist as exc:
        raise ValidationError("HOD user not found.") from exc
    if u.role != UserRole.HOD:
        raise ValidationError("Linked user must have HOD role.")
    return u
