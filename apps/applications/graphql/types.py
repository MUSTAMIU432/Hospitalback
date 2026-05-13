import strawberry
import strawberry_django
from strawberry.types import Info
from strawberry_django.auth.utils import get_current_user

from apps.applications.models import Application, ApplicationDocument, ChangeRequest, ChangeRequestTarget, ReviewTrail
from apps.applications.services.workflow import user_can_see_internal_change_requests
from apps.hospital_directory.graphql.types import DepartmentType
from apps.students.models import StudentProfile
from apps.users.graphql.types import UserType  # noqa: F401 — GraphQL type for reviewer/applicant


@strawberry.type
class ApplicantStudentProfileType:
    full_name: str
    registration_no: str
    programme: str
    faculty: str
    year_of_study: int
    gender: str
    level_of_study: str


@strawberry.type
class PdfPayload:
    filename: str
    content_base64: str


@strawberry.type
class EncodedFilePayload:
    """Binary or text file returned as base64 for authenticated download (GraphQL transport)."""

    filename: str
    content_base64: str
    mime_type: str = "application/octet-stream"


@strawberry_django.type(
    ApplicationDocument,
    fields=["id", "doc_type", "file", "uploaded_at"],
)
class ApplicationDocumentType:
    """Omit ``application`` to avoid circular schema issues when nested under Application."""


@strawberry_django.type(
    ChangeRequest,
    fields=["id", "target", "message", "reply_contact_email", "notify_via_system", "notify_via_email", "created_at"],
)
class ChangeRequestType:
    @strawberry_django.field()
    def sender(self, root: ChangeRequest) -> UserType:
        from apps.users.models import User
        return User.objects.get(pk=root.sender_id)


@strawberry_django.type(
    ReviewTrail,
    fields=[
        "id",
        "stage",
        "decision",
        "remarks",
        "letter_body",
        "signature_data",
        "feedback_target",
        "reviewed_at",
    ],
)
class ReviewTrailType:
    """Omit ``application`` (circular). ``reviewer`` resolved as UserType below."""

    @strawberry_django.field()
    def reviewer(self, root: ReviewTrail) -> UserType:
        from apps.users.models import User

        return User.objects.get(pk=root.reviewer_id)


@strawberry_django.type(
    Application,
    fields=[
        "id",
        "app_ref",
        "app_type",
        "status",
        "current_stage",
        "submitted_at",
        "updated_at",
        "institution_name",
        "programme_applied",
        "start_date",
        "end_date",
        "sponsorship_type",
        "reason_for_study",
        "attachment_dept",
        "placement_scope",
        "attachment_start",
        "attachment_end",
        "supervisor_requested",
        "placement_conducted_site",
        "hr_feedback_for_university",
        "field_records_shared_at",
    ],
)
class ApplicationType:
    @strawberry_django.field()
    def hospital_department(self, root: Application) -> DepartmentType | None:
        if root.hospital_department_id is None:
            return None
        from apps.hospital_directory.models import Department

        return Department.objects.get(pk=root.hospital_department_id)

    @strawberry_django.field()
    def applicant(self, root: Application) -> UserType:
        from apps.users.models import User

        return User.objects.get(pk=root.applicant_id)

    @strawberry_django.field()
    def documents(self, root: Application) -> list[ApplicationDocumentType]:
        return list(root.documents.all())

    @strawberry_django.field()
    def reviews(self, root: Application) -> list[ReviewTrailType]:
        return list(
            root.reviews.select_related("reviewer").order_by("-reviewed_at")
        )

    @strawberry_django.field()
    def change_requests(self, root: Application, info: Info) -> list[ChangeRequestType]:
        """Excludes TM↔ADR internal coordination rows for roles that should not see them (e.g. HOD)."""
        user = get_current_user(info, strict=False)
        qs = root.change_requests.select_related("sender")
        internal = {ChangeRequestTarget.TO_ADR, ChangeRequestTarget.TO_MGMT}
        if not user_can_see_internal_change_requests(user):
            qs = qs.exclude(target__in=internal)
        return list(qs.order_by("-created_at"))

    @strawberry.field
    def applicant_student_profile(self, root: Application) -> ApplicantStudentProfileType | None:
        try:
            sp = StudentProfile.objects.get(user_id=root.applicant_id)
        except StudentProfile.DoesNotExist:
            return None
        return ApplicantStudentProfileType(
            full_name=sp.full_name,
            registration_no=sp.registration_no,
            programme=sp.programme,
            faculty=sp.faculty,
            year_of_study=sp.year_of_study,
            gender=sp.gender,
            level_of_study=sp.level_of_study or "",
        )
