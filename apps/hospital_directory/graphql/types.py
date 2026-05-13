import strawberry_django

from apps.hospital_directory.models import (
    ApplicationDocumentKind,
    Department,
    Designation,
    SponsorshipType,
    WorkingSite,
)


@strawberry_django.type(Department, fields=["id", "name", "code", "is_active", "sort_order"])
class DepartmentType:
    pass


@strawberry_django.type(Designation, fields=["id", "name", "is_active", "sort_order"])
class DesignationType:
    pass


@strawberry_django.type(WorkingSite, fields=["id", "name", "is_active", "sort_order"])
class WorkingSiteType:
    pass


@strawberry_django.type(SponsorshipType, fields=["id", "name", "is_active", "sort_order"])
class SponsorshipTypeType:
    pass


@strawberry_django.type(
    ApplicationDocumentKind, fields=["id", "code", "label", "is_active", "sort_order"]
)
class ApplicationDocumentKindType:
    pass
