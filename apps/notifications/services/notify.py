from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from apps.employees.models import DepartmentHodAssignment, HospitalStaff
from apps.notifications.models import Notification
from core.constants import NotificationType, UserRole


def _maybe_email_copy(*, recipient, subject: str, body: str, force: bool = False) -> None:
    if not force and not getattr(settings, "STUD_EMAIL_NOTIFICATIONS", False):
        return
    email = (getattr(recipient, "email", None) or "").strip()
    if not email:
        return
    try:
        send_mail(
            subject,
            body,
            getattr(settings, "DEFAULT_FROM_EMAIL", None),
            [email],
            fail_silently=True,
        )
    except Exception:
        pass


def destination_for_application(*, user, application) -> str:
    role = getattr(user, "role", "")
    app_id = str(application.id)
    if role == UserRole.STUDENT:
        return f"/student/applications/{app_id}"
    if role in (UserRole.HOD, UserRole.ASST_DIRECTOR, UserRole.MANAGEMENT):
        return f"/reviewer/applications/{app_id}/review"
    if role == UserRole.HOSPITAL_STAFF:
        # hospital_staff with reviewer capabilities land on the reviewer page
        from apps.employees.services.capabilities import user_has_staff_capability
        if (
            user_has_staff_capability(user, "hod_assess_details")
            or user_has_staff_capability(user, "adr_assess_details")
            or user_has_staff_capability(user, "top_assess_details")
        ):
            return f"/reviewer/applications/{app_id}/review"
        return f"/hospital-staff/applications/{app_id}"
    if role == UserRole.HOSPITAL_ADMIN:
        return f"/admin/field-requests/{app_id}"
    return ""


def notify_user(
    *,
    recipient,
    message: str,
    notif_type: str,
    destination_path: str = "",
    sender=None,
) -> Notification:
    n = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        message=message,
        notif_type=notif_type,
        destination_path=(destination_path or "").strip(),
    )
    _maybe_email_copy(
        recipient=recipient,
        subject=f"STUD notification ({notif_type})",
        body=message,
    )
    return n


def send_email_copy(*, recipient, subject: str, body: str) -> None:
    """Explicit email channel (independent of in-app notifications)."""
    _maybe_email_copy(recipient=recipient, subject=subject, body=body, force=True)


def notify_users(
    *,
    recipients,
    message: str,
    notif_type: str,
    destination_path: str = "",
    sender=None,
) -> list[Notification]:
    return [
        notify_user(
            recipient=u,
            message=message,
            notif_type=notif_type,
            destination_path=destination_path,
            sender=sender,
        )
        for u in recipients
    ]


def _users_with_roles(*roles: str):
    User = get_user_model()
    return list(User.objects.filter(role__in=roles, is_active=True))


def notify_hod_for_submission(application) -> None:
    ref = application.app_ref or str(application.id)
    applicant_department_id = getattr(
        getattr(application.applicant, "hospital_staff_profile", None),
        "department_id",
        None,
    )
    if not applicant_department_id:
        return
    assignment_hod_ids = list(
        DepartmentHodAssignment.objects.filter(
            department_id=applicant_department_id,
            is_active=True,
        ).values_list("hod_user_id", flat=True)
    )
    fallback_hod_ids = list(
        HospitalStaff.objects.filter(
            user__role=UserRole.HOD,
            user__is_active=True,
            department_id=applicant_department_id,
        ).values_list("user_id", flat=True)
    )
    hod_ids = set(assignment_hod_ids + fallback_hod_ids)
    User = get_user_model()
    recipients = list(User.objects.filter(id__in=hod_ids, is_active=True))
    if not recipients:
        return
    notify_users(
        recipients=recipients,
        message=f"Application {ref} submitted and awaits HOD review.",
        notif_type=NotificationType.SUBMISSION,
        destination_path=f"/reviewer/applications/{application.id}/review",
    )


def _users_with_capability(capability: str):
    from apps.employees.services.capabilities import users_with_staff_capability
    return users_with_staff_capability(capability)


def _asst_director_recipients():
    """All users who act as Assistant Director — by role or by capability."""
    by_role = _users_with_roles(UserRole.ASST_DIRECTOR)
    by_cap  = _users_with_capability("adr_assess_details")
    seen = {u.id for u in by_role}
    return by_role + [u for u in by_cap if u.id not in seen]


def _management_recipients():
    """All users who act as Top Management — by role or by capability."""
    by_role = _users_with_roles(UserRole.MANAGEMENT)
    by_cap  = _users_with_capability("top_review_adr_fb")
    seen = {u.id for u in by_role}
    return by_role + [u for u in by_cap if u.id not in seen]


def _hod_recipients_for_application(application):
    """HOD users assigned to the applicant's department."""
    applicant_department_id = getattr(
        getattr(application.applicant, "hospital_staff_profile", None),
        "department_id",
        None,
    )
    if not applicant_department_id:
        return []
    assignment_hod_ids = list(
        DepartmentHodAssignment.objects.filter(
            department_id=applicant_department_id,
            is_active=True,
        ).values_list("hod_user_id", flat=True)
    )
    cap_hod_ids = list(
        HospitalStaff.objects.filter(
            department_id=applicant_department_id,
        ).values_list("user_id", flat=True)
    )
    from apps.employees.services.capabilities import users_with_staff_capability
    cap_hod_users = {u.id: u for u in users_with_staff_capability("hod_assess_details")}
    all_ids = set(assignment_hod_ids) | (set(cap_hod_ids) & set(cap_hod_users.keys()))
    User = get_user_model()
    return list(User.objects.filter(id__in=all_ids, is_active=True))


def notify_asst_directors_for_application(application, message: str | None = None) -> None:
    ref = application.app_ref or str(application.id)
    notify_users(
        recipients=_asst_director_recipients(),
        message=message or f"Application {ref} is awaiting Assistant Director review.",
        notif_type=NotificationType.SUBMISSION,
        destination_path=f"/reviewer/applications/{application.id}/review",
    )


def notify_management_for_application(application, message: str | None = None) -> None:
    ref = application.app_ref or str(application.id)
    notify_users(
        recipients=_management_recipients(),
        message=message or f"Application {ref} is awaiting Management review.",
        notif_type=NotificationType.SUBMISSION,
        destination_path=f"/reviewer/applications/{application.id}/review",
    )


def notify_hr_for_attachment(application) -> None:
    """Student field attachment submitted — HR capability holders and hospital admins."""
    from apps.employees.services.capabilities import users_with_staff_capability
    from core.constants import StaffCapability

    ref = application.app_ref or str(application.id)
    msg = f"Field attachment request {ref} was submitted and awaits HR processing."
    hr_users = users_with_staff_capability(StaffCapability.HR_FIELD_REQUESTS.value)
    notify_users(
        recipients=hr_users,
        message=msg,
        notif_type=NotificationType.SUBMISSION,
        destination_path=f"/hospital-staff/field-requests/{application.id}",
    )
    admins = _users_with_roles(UserRole.HOSPITAL_ADMIN)
    notify_users(
        recipients=admins,
        message=msg,
        notif_type=NotificationType.SUBMISSION,
        destination_path=f"/admin/field-requests/{application.id}",
    )


def notify_univ_admins_field_placement(application) -> None:
    """After HR approves attachment with a confirmed training site."""
    from apps.students.models import StudentProfile

    ref = application.app_ref or str(application.id)
    site = (application.placement_conducted_site or "").strip()
    stud = None
    try:
        stud = StudentProfile.objects.get(user_id=application.applicant_id)
    except StudentProfile.DoesNotExist:
        pass
    name = stud.full_name if stud else application.applicant.get_full_name()
    programme = stud.programme if stud else ""
    year = stud.year_of_study if stud else ""
    msg = (
        f"Field placement published — {ref}. Student: {name}. Programme: {programme}. "
        f"Year of study: {year}. Training conducted at: {site}."
    )
    if (application.hr_feedback_for_university or "").strip():
        msg += f" HR notes: {application.hr_feedback_for_university.strip()}"
    notify_users(
        recipients=_users_with_roles(UserRole.UNIV_ADMIN),
        message=msg,
        notif_type=NotificationType.FIELD_PLACEMENT_PUBLISHED,
        destination_path="/admin/field-placements",
    )


def notify_applicant(application, message: str, notif_type: str) -> None:
    notify_user(
        recipient=application.applicant,
        message=message,
        notif_type=notif_type,
        destination_path=destination_for_application(user=application.applicant, application=application),
    )
