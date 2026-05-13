import uuid

import strawberry
from django.core.exceptions import PermissionDenied
from strawberry.types import Info

from apps.employees.graphql.types import (
    DepartmentHodAssignmentType,
    HospitalStaffType,
    StaffCapabilityType,
    StaffRoleType,
)
from apps.employees.models import (
    DepartmentHodAssignment,
    HospitalStaff,
    StaffCapability,
    StaffRole,
    StaffRoleCapability,
)
from apps.employees.services.capabilities import user_has_staff_capability
from apps.users.graphql.auth import require_auth
from core.constants import StaffCapability as StaffCapabilityCode
from core.constants import UserRole


@strawberry.type
class HospitalStaffQuery:
    @strawberry.field
    def hospital_staff(self, info: Info) -> list[HospitalStaffType]:
        user = require_auth(info)
        role = getattr(user, "role", None)
        if role != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Not allowed to list hospital staff.")
        return list(HospitalStaff.objects.all()[:500])

    @strawberry.field
    def my_hospital_staff_profile(self, info: Info) -> HospitalStaffType | None:
        user = require_auth(info)
        if getattr(user, "role", None) != UserRole.HOSPITAL_STAFF:
            return None
        return HospitalStaff.objects.filter(user=user).select_related(
            "department", "designation", "working_site"
        ).first()

    @strawberry.field
    def staff_roles(self, info: Info, active_only: bool = True) -> list[StaffRoleType]:
        require_auth(info)
        qs = StaffRole.objects.all().order_by("sort_order", "name")
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs)

    @strawberry.field
    def staff_capabilities(self, info: Info, active_only: bool = True) -> list[StaffCapabilityType]:
        require_auth(info)
        qs = StaffCapability.objects.all().order_by("module", "sort_order", "label")
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs)

    @strawberry.field
    def role_capability_ids(self, info: Info, role_id: uuid.UUID) -> list[str]:
        require_auth(info)
        return [
            str(cid)
            for cid in StaffRoleCapability.objects.filter(role_id=role_id, is_active=True).values_list(
                "capability_id", flat=True
            )
        ]

    @strawberry.field
    def department_hod_assignments(
        self, info: Info, active_only: bool = True
    ) -> list[DepartmentHodAssignmentType]:
        user = require_auth(info)
        if getattr(user, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can manage department HOD assignments.")
        qs = DepartmentHodAssignment.objects.select_related("department", "hod_user").order_by(
            "department__name"
        )
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs)

    @strawberry.field
    def my_department_staff(self, info: Info) -> list[HospitalStaffType]:
        user = require_auth(info)
        if not user_has_staff_capability(user, StaffCapabilityCode.HOD_VIEW_DEPARTMENT_STAFF.value):
            raise PermissionDenied("Missing capability to view department staff.")
        assigned_department_ids = set(
            DepartmentHodAssignment.objects.filter(
                hod_user_id=user.id,
                is_active=True,
            ).values_list("department_id", flat=True)
        )
        if not assigned_department_ids:
            own_department_id = getattr(getattr(user, "hospital_staff_profile", None), "department_id", None)
            if own_department_id:
                assigned_department_ids.add(own_department_id)
        if not assigned_department_ids:
            return []
        return list(
            HospitalStaff.objects.select_related("department", "designation", "working_site", "staff_role", "user")
            .filter(department_id__in=assigned_department_ids, user__is_active=True)
            .exclude(user_id=user.id)
            .order_by("full_name")[:1000]
        )

    @strawberry.field
    def hod_candidates_for_department_assignment(self, info: Info) -> list[HospitalStaffType]:
        user = require_auth(info)
        if getattr(user, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can view HOD candidates.")
        # Dynamic capability-driven source: candidates are users that can review HOD stage.
        reviewer_role_ids = StaffRoleCapability.objects.filter(
            is_active=True,
            capability__is_active=True,
            capability__code="hod_assess_details",
        ).values_list("role_id", flat=True)
        return list(
            HospitalStaff.objects.select_related("department", "designation", "working_site", "staff_role", "user")
            .filter(user__is_active=True, staff_role_id__in=reviewer_role_ids)
            .order_by("full_name")[:1000]
        )
