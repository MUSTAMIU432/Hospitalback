import strawberry_django

from apps.hospital_directory.graphql.types import DepartmentType
from apps.students.models import StudentProfile, UniversityDepartment, UniversityFaculty
from apps.users.graphql.types import UserType


@strawberry_django.type(UniversityFaculty, fields=["id", "name", "is_active", "sort_order"])
class UniversityFacultyType:
    pass


@strawberry_django.type(UniversityDepartment, fields=["id", "name", "is_active", "sort_order"])
class UniversityDepartmentType:
    @strawberry_django.field()
    def faculty(self, root: UniversityDepartment) -> UniversityFacultyType:
        return UniversityFaculty.objects.get(pk=root.faculty_id)


@strawberry_django.type(
    StudentProfile,
    fields=[
        "id",
        "registration_no",
        "full_name",
        "programme",
        "faculty",
        "year_of_study",
        "phone",
        "contact_email",
        "gender",
        "dob",
        "university",
        "dashboard_notes",
        "level_of_study",
    ],
)
class StudentProfileType:
    @strawberry_django.field()
    def is_active(self, root: StudentProfile) -> bool:
        # user is select_related in the query so no extra hit
        try:
            return root.user.is_active
        except Exception:
            return False

    @strawberry_django.field()
    def hospital_department(self, root: StudentProfile) -> DepartmentType | None:
        if root.hospital_department_id is None:
            return None
        from apps.hospital_directory.models import Department

        return Department.objects.get(pk=root.hospital_department_id)

    @strawberry_django.field()
    def user(self, root: StudentProfile) -> UserType:
        return root.user

    @strawberry_django.field()
    def supervisor(self, root: StudentProfile) -> UserType | None:
        if root.supervisor_id is None:
            return None
        return root.supervisor

    @strawberry_django.field()
    def faculty_entity(self, root: StudentProfile) -> UniversityFacultyType | None:
        if root.faculty_entity_id is None:
            return None
        return UniversityFaculty.objects.get(pk=root.faculty_entity_id)

    @strawberry_django.field()
    def department_entity(self, root: StudentProfile) -> UniversityDepartmentType | None:
        if root.department_entity_id is None:
            return None
        return UniversityDepartment.objects.get(pk=root.department_entity_id)
