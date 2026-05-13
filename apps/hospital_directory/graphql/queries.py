import strawberry
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


@strawberry.type
class HospitalDirectoryQuery:
    @strawberry.field
    def departments(self, info: Info, active_only: bool = True) -> list[DepartmentType]:
        require_auth(info)
        qs = Department.objects.all().order_by("sort_order", "name")
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs)

    @strawberry.field
    def designations(self, info: Info, active_only: bool = True) -> list[DesignationType]:
        require_auth(info)
        qs = Designation.objects.all().order_by("sort_order", "name")
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs)

    @strawberry.field
    def working_sites(self, info: Info, active_only: bool = True) -> list[WorkingSiteType]:
        require_auth(info)
        qs = WorkingSite.objects.all().order_by("sort_order", "name")
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs)

    @strawberry.field
    def sponsorship_types(self, info: Info, active_only: bool = True) -> list[SponsorshipTypeType]:
        require_auth(info)
        qs = SponsorshipType.objects.all().order_by("sort_order", "name")
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs)

    @strawberry.field
    def application_document_kinds(
        self, info: Info, active_only: bool = True
    ) -> list[ApplicationDocumentKindType]:
        require_auth(info)
        qs = ApplicationDocumentKind.objects.all().order_by("sort_order", "code")
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs)
