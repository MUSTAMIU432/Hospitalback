from datetime import date

import strawberry
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models.deletion import ProtectedError
from strawberry.types import Info

from apps.hospital_directory.models import Department, Designation, WorkingSite
from apps.employees.graphql.inputs import (
    CreateHospitalStaffInput,
    SetRoleCapabilitiesInput,
    UpsertDepartmentHodAssignmentInput,
    UpdateHospitalStaffCapabilitiesInput,
)
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
    StaffCapabilityOverride,
    StaffRole,
    StaffRoleCapability,
)
from apps.users.graphql.auth import require_auth
from apps.users.graphql.types import OperationResult
from apps.users.graphql.types import UserType
from apps.users.models import User
from apps.users.services import provisioning
from core.constants import HOSPITAL_WORKER_ROLES, UserRole


@strawberry.type
class HospitalStaffMutation:
    @strawberry.mutation
    def create_hospital_staff(self, info: Info, data: CreateHospitalStaffInput) -> UserType:
        acting = require_auth(info)
        user, _profile = provisioning.create_hospital_staff_user(
            acting_user=acting,
            staff_number=data.staff_number,
            national_id=data.national_id,
            full_name=data.full_name,
            department_id=data.department_id,
            designation_id=data.designation_id,
            working_site_id=data.working_site_id,
            staff_role_id=data.staff_role_id,
            phone=data.phone,
            date_employed=data.date_employed,
            email=data.email,
        )
        return user

    @strawberry.mutation
    def update_hospital_staff_capabilities(
        self, info: Info, data: UpdateHospitalStaffCapabilitiesInput
    ) -> HospitalStaffType:
        """Legacy compat: now writes per-staff override grants."""
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can update staff capabilities.")
        try:
            user = User.objects.get(pk=data.user_id)
        except User.DoesNotExist as exc:
            raise ValidationError("User not found.") from exc
        if getattr(user, "role", None) not in HOSPITAL_WORKER_ROLES:
            raise ValidationError("Capabilities apply only to hospital staff users.")
        try:
            profile = HospitalStaff.objects.get(user=user)
        except HospitalStaff.DoesNotExist as exc:
            raise ValidationError("Hospital staff profile not found.") from exc
        StaffCapabilityOverride.objects.filter(staff=profile, mode=StaffCapabilityOverride.MODE_GRANT).delete()
        for code in data.capabilities or []:
            cap = StaffCapability.objects.filter(code=code).first()
            if cap:
                StaffCapabilityOverride.objects.create(
                    staff=profile,
                    capability=cap,
                    mode=StaffCapabilityOverride.MODE_GRANT,
                    is_active=True,
                )
        profile.capabilities = list(data.capabilities or [])
        profile.save(update_fields=["capabilities"])
        return profile

    @strawberry.mutation
    def update_hospital_staff_record(
        self,
        info: Info,
        user_id: strawberry.ID,
        staff_number: str | None = None,
        national_id: str | None = None,
        full_name: str | None = None,
        phone: str | None = None,
        date_employed: date | None = None,
        email: str | None = None,
        department_id: strawberry.ID | None = None,
        designation_id: strawberry.ID | None = None,
        working_site_id: strawberry.ID | None = None,
        staff_role_id: strawberry.ID | None = None,
    ) -> HospitalStaffType:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can edit hospital staff.")
        user = User.objects.get(pk=user_id)
        if getattr(user, "role", None) not in HOSPITAL_WORKER_ROLES:
            raise ValidationError("Target user is not a hospital worker.")
        profile = HospitalStaff.objects.select_related("user").get(user=user)
        if staff_number is not None:
            sn = staff_number.strip()
            if not sn:
                raise ValidationError("Staff number cannot be blank.")
            dup = User.objects.filter(username=sn).exclude(pk=user.pk).exists()
            if dup:
                raise ValidationError("Another user already uses this staff number.")
            profile.staff_number = sn
            user.username = sn
        if national_id is not None:
            profile.national_id = national_id.strip()
        if full_name is not None:
            profile.full_name = full_name.strip()
        if phone is not None:
            profile.phone = phone.strip()
        if date_employed is not None:
            profile.date_employed = date_employed
        if department_id is not None:
            profile.department = Department.objects.get(pk=department_id)
        if designation_id is not None:
            profile.designation = Designation.objects.get(pk=designation_id)
        if working_site_id is not None:
            profile.working_site = WorkingSite.objects.get(pk=working_site_id)
        if staff_role_id is not None:
            profile.staff_role = StaffRole.objects.get(pk=staff_role_id, is_active=True)
        profile.full_clean()
        profile.save()
        if staff_number is not None:
            user.save(update_fields=["username"])
        if email is not None:
            user.email = email.strip()
            user.save(update_fields=["email"])
        return profile

    @strawberry.mutation
    def deactivate_hospital_staff_user(self, info: Info, user_id: strawberry.ID) -> UserType:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can deactivate staff users.")
        user = User.objects.get(pk=user_id)
        if getattr(user, "role", None) not in HOSPITAL_WORKER_ROLES:
            raise ValidationError("Target user is not a hospital worker.")
        user.is_active = False
        user.save(update_fields=["is_active"])
        return user

    @strawberry.mutation
    def activate_hospital_staff_user(self, info: Info, user_id: strawberry.ID) -> UserType:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can activate staff users.")
        user = User.objects.get(pk=user_id)
        if getattr(user, "role", None) not in HOSPITAL_WORKER_ROLES:
            raise ValidationError("Target user is not a hospital worker.")
        user.is_active = True
        user.save(update_fields=["is_active"])
        return user

    @strawberry.mutation
    def permanently_delete_hospital_staff_user(self, info: Info, user_id: strawberry.ID) -> OperationResult:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can permanently delete staff users.")
        user = User.objects.get(pk=user_id)
        if getattr(user, "role", None) not in HOSPITAL_WORKER_ROLES:
            raise ValidationError("Target user is not a hospital worker.")
        user.delete()
        return OperationResult(ok=True, message="Hospital staff user deleted permanently.")

    @strawberry.mutation
    def create_staff_role(
        self, info: Info, code: str, name: str, description: str = "", sort_order: int = 0
    ) -> StaffRoleType:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can manage staff roles.")
        c = code.strip().lower()
        if not c:
            raise ValidationError("Role code is required.")
        if StaffRole.objects.filter(code=c).exists():
            raise ValidationError("Role code already exists.")
        return StaffRole.objects.create(
            code=c,
            name=name.strip(),
            description=(description or "").strip(),
            sort_order=sort_order,
            is_active=True,
        )

    @strawberry.mutation
    def update_staff_role(
        self,
        info: Info,
        role_id: strawberry.ID,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
        sort_order: int | None = None,
    ) -> StaffRoleType:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can manage staff roles.")
        role = StaffRole.objects.get(pk=role_id)
        if name is not None:
            role.name = name.strip()
        if description is not None:
            role.description = description.strip()
        if is_active is not None:
            role.is_active = is_active
        if sort_order is not None:
            role.sort_order = sort_order
        role.save()
        return role

    @strawberry.mutation
    def permanently_delete_staff_role(self, info: Info, role_id: strawberry.ID) -> OperationResult:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can manage staff roles.")
        role = StaffRole.objects.get(pk=role_id)
        try:
            role.delete()
        except ProtectedError as exc:
            raise ValidationError("This role is still assigned to staff and cannot be permanently deleted.") from exc
        return OperationResult(ok=True, message="Role deleted permanently.")

    @strawberry.mutation
    def create_staff_capability(
        self,
        info: Info,
        code: str,
        label: str,
        module: str = "general",
        description: str = "",
        sort_order: int = 0,
    ) -> StaffCapabilityType:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can manage capabilities.")
        c = code.strip().lower()
        if not c:
            raise ValidationError("Capability code is required.")
        if StaffCapability.objects.filter(code=c).exists():
            raise ValidationError("Capability code already exists.")
        return StaffCapability.objects.create(
            code=c,
            label=label.strip(),
            module=(module or "general").strip() or "general",
            description=(description or "").strip(),
            sort_order=sort_order,
            is_active=True,
        )

    @strawberry.mutation
    def update_staff_capability(
        self,
        info: Info,
        capability_id: strawberry.ID,
        code: str | None = None,
        label: str | None = None,
        module: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
        sort_order: int | None = None,
    ) -> StaffCapabilityType:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can manage capabilities.")
        cap = StaffCapability.objects.get(pk=capability_id)
        if code is not None:
            next_code = code.strip().lower()
            if not next_code:
                raise ValidationError("Capability code is required.")
            dup = StaffCapability.objects.filter(code=next_code).exclude(pk=cap.pk).exists()
            if dup:
                raise ValidationError("Capability code already exists.")
            cap.code = next_code
        if label is not None:
            cap.label = label.strip()
        if module is not None:
            cap.module = (module or "general").strip() or "general"
        if description is not None:
            cap.description = description.strip()
        if is_active is not None:
            cap.is_active = is_active
        if sort_order is not None:
            cap.sort_order = sort_order
        cap.save()
        return cap

    @strawberry.mutation
    def delete_staff_capability(self, info: Info, capability_id: strawberry.ID) -> bool:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can manage capabilities.")
        StaffCapability.objects.filter(pk=capability_id).delete()
        return True

    @strawberry.mutation
    def set_role_capabilities(self, info: Info, data: SetRoleCapabilitiesInput) -> StaffRoleType:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can map role capabilities.")
        role = StaffRole.objects.get(pk=data.role_id)
        wanted = set(data.capability_ids or [])
        StaffRoleCapability.objects.filter(role=role).exclude(capability_id__in=wanted).delete()
        existing = set(StaffRoleCapability.objects.filter(role=role).values_list("capability_id", flat=True))
        for cid in wanted - existing:
            cap = StaffCapability.objects.get(pk=cid)
            StaffRoleCapability.objects.create(role=role, capability=cap, is_active=True)
        return role

    @strawberry.mutation
    def upsert_department_hod_assignment(
        self, info: Info, data: UpsertDepartmentHodAssignmentInput
    ) -> DepartmentHodAssignmentType:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can assign departments to HODs.")
        department = Department.objects.get(pk=data.department_id)
        hod_user = User.objects.get(pk=data.hod_user_id, is_active=True)
        if getattr(hod_user, "role", None) not in HOSPITAL_WORKER_ROLES:
            raise ValidationError("Selected user is not an active hospital worker.")
        assignment, _ = DepartmentHodAssignment.objects.update_or_create(
            department=department,
            defaults={"hod_user": hod_user, "is_active": data.is_active},
        )
        return assignment

    @strawberry.mutation
    def remove_department_hod_assignment(self, info: Info, department_id: strawberry.ID) -> OperationResult:
        acting = require_auth(info)
        if getattr(acting, "role", None) != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Only hospital admin can remove department HOD assignments.")
        DepartmentHodAssignment.objects.filter(department_id=department_id).delete()
        return OperationResult(ok=True, message="Department HOD assignment removed.")
