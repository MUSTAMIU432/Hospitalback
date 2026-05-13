import uuid

import strawberry
from django.core.exceptions import PermissionDenied, ValidationError
from strawberry.types import Info

from apps.hospital_directory.graphql.types import (
    ApplicationDocumentKindType,
    DepartmentType,
    DesignationType,
    SponsorshipTypeType,
    WorkingSiteType,
)
from apps.hospital_directory.models import (
    ApplicationDocumentKind,
    Department,
    Designation,
    SponsorshipType,
    WorkingSite,
)
from apps.users.graphql.auth import require_auth
from core.constants import UserRole


def _require_directory_admin(info: Info):
    user = require_auth(info)
    role = getattr(user, "role", None)
    if role != UserRole.HOSPITAL_ADMIN:
        raise PermissionDenied("Not allowed to manage hospital directory.")
    return user


@strawberry.type
class HospitalDirectoryMutation:
    @strawberry.mutation
    def create_department(
        self,
        info: Info,
        name: str,
        code: str = "",
        sort_order: int = 0,
    ) -> DepartmentType:
        _require_directory_admin(info)
        if Department.objects.filter(name__iexact=name.strip()).exists():
            raise ValidationError("Department with this name already exists.")
        return Department.objects.create(
            name=name.strip(),
            code=code.strip(),
            sort_order=sort_order,
        )

    @strawberry.mutation
    def update_department(
        self,
        info: Info,
        department_id: uuid.UUID,
        name: str | None = None,
        code: str | None = None,
        is_active: bool | None = None,
        sort_order: int | None = None,
    ) -> DepartmentType:
        _require_directory_admin(info)
        d = Department.objects.get(pk=department_id)
        if name is not None:
            d.name = name.strip()
        if code is not None:
            d.code = code.strip()
        if is_active is not None:
            d.is_active = is_active
        if sort_order is not None:
            d.sort_order = sort_order
        d.save()
        return d

    @strawberry.mutation
    def create_designation(
        self, info: Info, name: str, sort_order: int = 0
    ) -> DesignationType:
        _require_directory_admin(info)
        if Designation.objects.filter(name__iexact=name.strip()).exists():
            raise ValidationError("Designation already exists.")
        return Designation.objects.create(name=name.strip(), sort_order=sort_order)

    @strawberry.mutation
    def update_designation(
        self,
        info: Info,
        designation_id: uuid.UUID,
        name: str | None = None,
        is_active: bool | None = None,
        sort_order: int | None = None,
    ) -> DesignationType:
        _require_directory_admin(info)
        d = Designation.objects.get(pk=designation_id)
        if name is not None:
            d.name = name.strip()
        if is_active is not None:
            d.is_active = is_active
        if sort_order is not None:
            d.sort_order = sort_order
        d.save()
        return d

    @strawberry.mutation
    def create_working_site(self, info: Info, name: str, sort_order: int = 0) -> WorkingSiteType:
        _require_directory_admin(info)
        if WorkingSite.objects.filter(name__iexact=name.strip()).exists():
            raise ValidationError("Working site already exists.")
        return WorkingSite.objects.create(name=name.strip(), sort_order=sort_order)

    @strawberry.mutation
    def update_working_site(
        self,
        info: Info,
        site_id: uuid.UUID,
        name: str | None = None,
        is_active: bool | None = None,
        sort_order: int | None = None,
    ) -> WorkingSiteType:
        _require_directory_admin(info)
        s = WorkingSite.objects.get(pk=site_id)
        if name is not None:
            s.name = name.strip()
        if is_active is not None:
            s.is_active = is_active
        if sort_order is not None:
            s.sort_order = sort_order
        s.save()
        return s

    @strawberry.mutation
    def create_sponsorship_type(
        self, info: Info, name: str, sort_order: int = 0
    ) -> SponsorshipTypeType:
        _require_directory_admin(info)
        n = name.strip()
        if SponsorshipType.objects.filter(name__iexact=n).exists():
            raise ValidationError("Sponsorship type already exists.")
        return SponsorshipType.objects.create(name=n, sort_order=sort_order)

    @strawberry.mutation
    def update_sponsorship_type(
        self,
        info: Info,
        sponsorship_type_id: uuid.UUID,
        name: str | None = None,
        is_active: bool | None = None,
        sort_order: int | None = None,
    ) -> SponsorshipTypeType:
        _require_directory_admin(info)
        s = SponsorshipType.objects.get(pk=sponsorship_type_id)
        if name is not None:
            s.name = name.strip()
        if is_active is not None:
            s.is_active = is_active
        if sort_order is not None:
            s.sort_order = sort_order
        s.save()
        return s

    @strawberry.mutation
    def create_application_document_kind(
        self, info: Info, code: str, label: str, sort_order: int = 0
    ) -> ApplicationDocumentKindType:
        _require_directory_admin(info)
        c = code.strip().lower().replace(" ", "_")
        if not c:
            raise ValidationError("Code is required.")
        if ApplicationDocumentKind.objects.filter(code=c).exists():
            raise ValidationError("Document kind code already exists.")
        return ApplicationDocumentKind.objects.create(
            code=c, label=label.strip(), sort_order=sort_order
        )

    @strawberry.mutation
    def update_application_document_kind(
        self,
        info: Info,
        kind_id: uuid.UUID,
        label: str | None = None,
        is_active: bool | None = None,
        sort_order: int | None = None,
    ) -> ApplicationDocumentKindType:
        _require_directory_admin(info)
        k = ApplicationDocumentKind.objects.get(pk=kind_id)
        if label is not None:
            k.label = label.strip()
        if is_active is not None:
            k.is_active = is_active
        if sort_order is not None:
            k.sort_order = sort_order
        k.save()
        return k

    @strawberry.mutation
    def delete_department(self, info: Info, department_id: uuid.UUID) -> bool:
        _require_directory_admin(info)
        Department.objects.filter(pk=department_id).delete()
        return True

    @strawberry.mutation
    def delete_designation(self, info: Info, designation_id: uuid.UUID) -> bool:
        _require_directory_admin(info)
        Designation.objects.filter(pk=designation_id).delete()
        return True

    @strawberry.mutation
    def delete_working_site(self, info: Info, site_id: uuid.UUID) -> bool:
        _require_directory_admin(info)
        WorkingSite.objects.filter(pk=site_id).delete()
        return True

    @strawberry.mutation
    def delete_sponsorship_type(self, info: Info, sponsorship_type_id: uuid.UUID) -> bool:
        _require_directory_admin(info)
        SponsorshipType.objects.filter(pk=sponsorship_type_id).delete()
        return True

    @strawberry.mutation
    def delete_application_document_kind(self, info: Info, kind_id: uuid.UUID) -> bool:
        _require_directory_admin(info)
        ApplicationDocumentKind.objects.filter(pk=kind_id).delete()
        return True
