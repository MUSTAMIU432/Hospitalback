import strawberry_django

from apps.employees.models import DepartmentHodAssignment, HospitalStaff, StaffCapability, StaffRole
from apps.hospital_directory.graphql.types import (
    DepartmentType,
    DesignationType,
    WorkingSiteType,
)
from apps.users.graphql.types import UserType


@strawberry_django.type(
    StaffRole,
    fields=["id", "code", "name", "description", "is_active", "sort_order"],
)
class StaffRoleType:
    pass


@strawberry_django.type(
    StaffCapability,
    fields=["id", "code", "label", "description", "module", "is_active", "sort_order"],
)
class StaffCapabilityType:
    pass


@strawberry_django.type(
    HospitalStaff,
    fields=[
        "id",
        "staff_number",
        "full_name",
        "phone",
        "national_id",
        "date_employed",
        "capabilities",
        "staff_role_id",
    ],
)
class HospitalStaffType:
    @strawberry_django.field()
    def department(self, root: HospitalStaff) -> DepartmentType | None:
        if root.department_id is None:
            return None
        from apps.hospital_directory.models import Department

        return Department.objects.get(pk=root.department_id)

    @strawberry_django.field()
    def designation(self, root: HospitalStaff) -> DesignationType | None:
        if root.designation_id is None:
            return None
        from apps.hospital_directory.models import Designation

        return Designation.objects.get(pk=root.designation_id)

    @strawberry_django.field()
    def working_site(self, root: HospitalStaff) -> WorkingSiteType | None:
        if root.working_site_id is None:
            return None
        from apps.hospital_directory.models import WorkingSite

        return WorkingSite.objects.get(pk=root.working_site_id)

    @strawberry_django.field()
    def user(self, root: HospitalStaff) -> UserType:
        from apps.users.models import User

        return User.objects.get(pk=root.user_id)

    @strawberry_django.field()
    def staff_role(self, root: HospitalStaff) -> StaffRoleType | None:
        if root.staff_role_id is None:
            return None
        return StaffRole.objects.get(pk=root.staff_role_id)


@strawberry_django.type(
    DepartmentHodAssignment,
    fields=["id", "is_active", "department_id", "hod_user_id", "created_at", "updated_at"],
)
class DepartmentHodAssignmentType:
    @strawberry_django.field()
    def department(self, root: DepartmentHodAssignment) -> DepartmentType | None:
        if root.department_id is None:
            return None
        from apps.hospital_directory.models import Department

        return Department.objects.get(pk=root.department_id)

    @strawberry_django.field()
    def hod_user(self, root: DepartmentHodAssignment) -> UserType | None:
        if root.hod_user_id is None:
            return None
        from apps.users.models import User

        return User.objects.get(pk=root.hod_user_id)
