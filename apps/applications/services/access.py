from django.db.models import Exists, OuterRef, Q, QuerySet

from apps.applications.models import Application, ReviewTrail
from apps.employees.models import HospitalStaff
from apps.employees.models import DepartmentHodAssignment
from apps.employees.services.capabilities import user_has_staff_capability
from core.constants import (
    ApplicationStatus,
    ApplicationType,
    ReviewStage,
    StaffCapability,
    UserRole,
)


def applications_for_applicant(user) -> QuerySet[Application]:
    return Application.objects.filter(applicant=user)


def _attachment_hr_stage_q() -> Q:
    return Q(
        app_type=ApplicationType.ATTACHMENT,
        status__in=(
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.RETURNED,
            ApplicationStatus.UNDER_REVIEW,
        ),
        current_stage=ReviewStage.HR,
    )


def _hod_department_ids(user) -> set:
    assigned = set(
        DepartmentHodAssignment.objects.filter(
            hod_user_id=user.id,
            is_active=True,
        ).values_list("department_id", flat=True)
    )
    if assigned:
        return assigned
    # Fallback: if explicit assignments are not configured yet, use the HOD's own staff profile department.
    own_department_id = getattr(getattr(user, "hospital_staff_profile", None), "department_id", None)
    if own_department_id:
        return {own_department_id}
    # Defensive fallback for stale relation caches.
    profile = HospitalStaff.objects.filter(user_id=user.id).values("department_id").first()
    dep = (profile or {}).get("department_id")
    return {dep} if dep else set()



def applications_in_review_queues(user) -> QuerySet[Application]:
    """Applications this user may act on as a reviewer (role + stage)."""
    role = getattr(user, "role", None)
    if role == UserRole.HOSPITAL_ADMIN:
        return Application.objects.filter(
            Q(
                app_type=ApplicationType.FURTHER_STUDIES,
                status=ApplicationStatus.UNDER_REVIEW,
                current_stage=ReviewStage.MANAGEMENT,
            )
            | _attachment_hr_stage_q()
        )

    if role == UserRole.HOSPITAL_STAFF and user_has_staff_capability(
        user, StaffCapability.HR_FIELD_REQUESTS.value
    ):
        return Application.objects.filter(_attachment_hr_stage_q())

    qs = Application.objects.none()
    is_hod_reviewer = role == UserRole.HOD or user_has_staff_capability(user, "hod_assess_details")
    is_adr_reviewer = role == UserRole.ASST_DIRECTOR or user_has_staff_capability(user, "adr_assess_details")
    is_mgmt_reviewer = role == UserRole.MANAGEMENT or user_has_staff_capability(user, "top_review_adr_fb")
    if is_hod_reviewer:
        department_ids = _hod_department_ids(user)
        if not department_ids:
            return Application.objects.none()
        qs = Application.objects.filter(
            app_type=ApplicationType.FURTHER_STUDIES,
            status__in=(
                ApplicationStatus.SUBMITTED,
                ApplicationStatus.UNDER_REVIEW,
            ),
            current_stage=ReviewStage.HOD,
            applicant__hospital_staff_profile__department_id__in=department_ids,
        ).exclude(applicant_id=user.id)
    elif is_adr_reviewer:
        qs = Application.objects.filter(
            app_type=ApplicationType.FURTHER_STUDIES,
            status=ApplicationStatus.UNDER_REVIEW,
            current_stage=ReviewStage.ASST_DIRECTOR,
        )
    elif is_mgmt_reviewer:
        # Top Management sees all further-studies applications currently at the management stage.
        qs = Application.objects.filter(
            app_type=ApplicationType.FURTHER_STUDIES,
            status=ApplicationStatus.UNDER_REVIEW,
            current_stage=ReviewStage.MANAGEMENT,
        ).order_by("-updated_at")
    return qs


def can_query_management_final_letters(user) -> bool:
    """Who may list stored Top Management final letters (/reviewer/final-letter)."""
    role = getattr(user, "role", "")
    if role in (UserRole.HOD, UserRole.ASST_DIRECTOR, UserRole.MANAGEMENT):
        return True
    return (
        user_has_staff_capability(user, "hod_view_final_letter")
        or user_has_staff_capability(user, "adr_view_final_letter")
    )


def applications_with_management_final_letters(user):
    """
    Further-studies applications that have a stored Top Management review letter body.
    Includes approved/archived items — not limited to the active review queue.
    """
    has_mgmt_letter = ReviewTrail.objects.filter(
        application_id=OuterRef("pk"),
        stage=ReviewStage.MANAGEMENT,
    ).exclude(letter_body="")
    qs = (
        Application.objects.filter(app_type=ApplicationType.FURTHER_STUDIES)
        .filter(Exists(has_mgmt_letter))
        .select_related("applicant")
        .order_by("-updated_at")
    )
    return [app for app in qs if can_view_application(user, app)]


def field_placements_visible_to_university() -> QuerySet[Application]:
    return Application.objects.filter(
        app_type=ApplicationType.ATTACHMENT,
        status=ApplicationStatus.APPROVED,
        field_records_shared_at__isnull=False,
    ).order_by("-field_records_shared_at")


def can_view_application(user, application: Application) -> bool:
    if not user.is_authenticated:
        return False
    role = getattr(user, "role", None)
    if role == UserRole.STUDENT:
        return application.applicant_id == user.id
    if application.applicant_id == user.id:
        return True
    if role == UserRole.HOSPITAL_ADMIN:
        return True
    # Keep queue visibility and detail-page visibility aligned:
    # if an item is in this user's review queue, they must be able to open it.
    is_reviewer_like = (
        role in (UserRole.HOD, UserRole.ASST_DIRECTOR, UserRole.MANAGEMENT)
        or user_has_staff_capability(user, "hod_assess_details")
        or user_has_staff_capability(user, "adr_assess_details")
        or user_has_staff_capability(user, "top_review_adr_fb")
    )
    if is_reviewer_like and applications_in_review_queues(user).filter(pk=application.pk).exists():
        return True
    if role == UserRole.ASST_DIRECTOR or user_has_staff_capability(user, "adr_assess_details"):
        return application.app_type == ApplicationType.FURTHER_STUDIES
    if role == UserRole.MANAGEMENT or user_has_staff_capability(user, "top_review_adr_fb"):
        return application.app_type == ApplicationType.FURTHER_STUDIES
    if role == UserRole.UNIV_ADMIN:
        if application.app_type != ApplicationType.ATTACHMENT:
            return False
        return (
            application.status == ApplicationStatus.APPROVED
            and application.field_records_shared_at is not None
        )
    is_hod_reviewer = role == UserRole.HOD or user_has_staff_capability(user, "hod_assess_details")
    if is_hod_reviewer:
        if application.app_type != ApplicationType.FURTHER_STUDIES:
            return False
        applicant_department_id = getattr(
            getattr(application.applicant, "hospital_staff_profile", None),
            "department_id",
            None,
        )
        if applicant_department_id is None:
            return False
        return applicant_department_id in _hod_department_ids(user)
    if role == UserRole.HOSPITAL_STAFF and user_has_staff_capability(
        user, StaffCapability.HR_FIELD_REQUESTS.value
    ):
        if application.app_type != ApplicationType.ATTACHMENT:
            return False
        return application.status in (
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.RETURNED,
            ApplicationStatus.UNDER_REVIEW,
        ) and application.current_stage == ReviewStage.HR
    return False
