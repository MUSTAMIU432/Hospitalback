import uuid

import strawberry
from django.core.exceptions import PermissionDenied
from strawberry.types import Info

from apps.students.graphql.types import (
    StudentProfileType,
    UniversityDepartmentType,
    UniversityFacultyType,
)
from apps.students.models import StudentProfile, UniversityDepartment, UniversityFaculty
from apps.users.graphql.auth import require_auth
from core.constants import STUDENT_MANAGER_ROLES, UserRole


@strawberry.type
class StudentsQuery:
    @strawberry.field
    def students(self, info: Info) -> list[StudentProfileType]:
        user = require_auth(info)
        role = getattr(user, "role", None)
        if role not in STUDENT_MANAGER_ROLES:
            raise PermissionDenied("Not allowed to list students.")
        return list(StudentProfile.objects.select_related("user", "supervisor").all()[:500])

    @strawberry.field
    def university_faculties(self, info: Info, active_only: bool = True) -> list[UniversityFacultyType]:
        require_auth(info)
        qs = UniversityFaculty.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs.order_by("sort_order", "name")[:200])

    @strawberry.field
    def university_departments(
        self, info: Info, faculty_id: uuid.UUID | None = None, active_only: bool = True
    ) -> list[UniversityDepartmentType]:
        require_auth(info)
        qs = UniversityDepartment.objects.select_related("faculty").all()
        if active_only:
            qs = qs.filter(is_active=True)
        if faculty_id is not None:
            qs = qs.filter(faculty_id=faculty_id)
        return list(qs.order_by("faculty", "sort_order", "name")[:500])
