import uuid

import strawberry
from django.core.exceptions import PermissionDenied, ValidationError
from strawberry.types import Info

from apps.students.graphql.inputs import CreateStudentInput
from apps.students.graphql.types import StudentProfileType, UniversityDepartmentType, UniversityFacultyType
from apps.students.models import StudentProfile, UniversityDepartment, UniversityFaculty
from apps.users.graphql.auth import require_auth
from apps.users.graphql.types import OperationResult, UserType
from apps.users.models import User
from apps.users.services import provisioning
from core.constants import STUDENT_MANAGER_ROLES, UserRole


def _require_univ_admin(info: Info):
    u = require_auth(info)
    if getattr(u, "role", None) != UserRole.UNIV_ADMIN:
        raise PermissionDenied("Only university administrators may manage this registry.")
    return u


def _require_student_manager(info: Info):
    u = require_auth(info)
    if getattr(u, "role", None) not in STUDENT_MANAGER_ROLES:
        raise PermissionDenied("Not allowed to manage student records.")
    return u


@strawberry.type
class StudentsMutation:
    @strawberry.mutation
    def create_student(self, info: Info, data: CreateStudentInput) -> UserType:
        acting = require_auth(info)
        sup = None
        if data.supervisor_user_id:
            sup = User.objects.filter(pk=data.supervisor_user_id).first()
        user, _profile = provisioning.create_student_user(
            acting_user=acting,
            registration_no=data.registration_no,
            full_name=data.full_name,
            programme=data.programme,
            faculty=data.faculty,
            year_of_study=data.year_of_study,
            phone=data.phone,
            dob=data.dob,
            university=data.university,
            supervisor_user=sup,
            email=data.email,
            contact_email=data.contact_email,
            gender=data.gender,
            hospital_department_id=data.hospital_department_id,
            dashboard_notes=data.dashboard_notes,
            faculty_entity_id=data.faculty_entity_id,
            department_entity_id=data.department_entity_id,
            level_of_study=data.level_of_study,
        )
        return user

    @strawberry.mutation
    def create_university_faculty(self, info: Info, name: str, sort_order: int = 0) -> UniversityFacultyType:
        _require_univ_admin(info)
        n = name.strip()
        if UniversityFaculty.objects.filter(name__iexact=n).exists():
            raise ValidationError("Faculty already exists.")
        return UniversityFaculty.objects.create(name=n, sort_order=sort_order)

    @strawberry.mutation
    def update_university_faculty(
        self,
        info: Info,
        faculty_id: uuid.UUID,
        name: str | None = None,
        is_active: bool | None = None,
        sort_order: int | None = None,
    ) -> UniversityFacultyType:
        _require_univ_admin(info)
        f = UniversityFaculty.objects.get(pk=faculty_id)
        if name is not None:
            f.name = name.strip()
        if is_active is not None:
            f.is_active = is_active
        if sort_order is not None:
            f.sort_order = sort_order
        f.save()
        return f

    @strawberry.mutation
    def create_university_department(
        self, info: Info, faculty_id: uuid.UUID, name: str, sort_order: int = 0
    ) -> UniversityDepartmentType:
        _require_univ_admin(info)
        fac = UniversityFaculty.objects.get(pk=faculty_id)
        n = name.strip()
        if UniversityDepartment.objects.filter(faculty=fac, name__iexact=n).exists():
            raise ValidationError("Department already exists for this faculty.")
        return UniversityDepartment.objects.create(faculty=fac, name=n, sort_order=sort_order)

    @strawberry.mutation
    def update_university_department(
        self,
        info: Info,
        department_id: uuid.UUID,
        name: str | None = None,
        is_active: bool | None = None,
        sort_order: int | None = None,
    ) -> UniversityDepartmentType:
        _require_univ_admin(info)
        d = UniversityDepartment.objects.get(pk=department_id)
        if name is not None:
            d.name = name.strip()
        if is_active is not None:
            d.is_active = is_active
        if sort_order is not None:
            d.sort_order = sort_order
        d.save()
        return d

    @strawberry.mutation
    def delete_university_faculty(self, info: Info, faculty_id: uuid.UUID) -> bool:
        _require_univ_admin(info)
        UniversityFaculty.objects.filter(pk=faculty_id).delete()
        return True

    @strawberry.mutation
    def delete_university_department(self, info: Info, department_id: uuid.UUID) -> bool:
        _require_univ_admin(info)
        UniversityDepartment.objects.filter(pk=department_id).delete()
        return True

    @strawberry.mutation
    def update_student_record(
        self,
        info: Info,
        user_id: strawberry.ID,
        full_name: str | None = None,
        registration_no: str | None = None,
        programme: str | None = None,
        faculty: str | None = None,
        year_of_study: int | None = None,
        university: str | None = None,
        phone: str | None = None,
        email: str | None = None,
    ) -> StudentProfileType:
        _require_student_manager(info)
        profile = StudentProfile.objects.select_related("user").get(pk=user_id)
        user = profile.user
        if full_name is not None:
            profile.full_name = full_name.strip()
        if registration_no is not None:
            rn = registration_no.strip()
            if not rn:
                raise ValidationError("Registration number cannot be blank.")
            dup = StudentProfile.objects.filter(registration_no__iexact=rn).exclude(pk=profile.pk).exists()
            if dup:
                raise ValidationError("Another student already uses this registration number.")
            profile.registration_no = rn
            user.username = rn
            user.save(update_fields=["username"])
        if programme is not None:
            profile.programme = programme.strip()
        if faculty is not None:
            profile.faculty = faculty.strip()
        if year_of_study is not None:
            profile.year_of_study = year_of_study
        if university is not None:
            profile.university = university.strip()
        if phone is not None:
            profile.phone = phone.strip()
        if email is not None:
            user.email = email.strip()
            user.save(update_fields=["email"])
        profile.save()
        return profile

    @strawberry.mutation
    def deactivate_student_user(self, info: Info, user_id: strawberry.ID) -> UserType:
        _require_student_manager(info)
        profile = StudentProfile.objects.select_related("user").get(pk=user_id)
        user = profile.user
        user.is_active = False
        user.save(update_fields=["is_active"])
        return user

    @strawberry.mutation
    def activate_student_user(self, info: Info, user_id: strawberry.ID) -> UserType:
        _require_student_manager(info)
        profile = StudentProfile.objects.select_related("user").get(pk=user_id)
        user = profile.user
        user.is_active = True
        user.save(update_fields=["is_active"])
        return user

    @strawberry.mutation
    def permanently_delete_student_user(self, info: Info, user_id: strawberry.ID) -> OperationResult:
        _require_student_manager(info)
        profile = StudentProfile.objects.select_related("user").get(pk=user_id)
        profile.user.delete()
        return OperationResult(ok=True, message="Student deleted permanently.")
