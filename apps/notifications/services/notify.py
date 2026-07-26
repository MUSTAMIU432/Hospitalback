import html as _html
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives

from apps.employees.models import DepartmentHodAssignment, HospitalStaff
from apps.notifications.models import Notification
from core.constants import NotificationType, UserRole


_APP_REF_RE = re.compile(r"\b(APP-\d{4}-\d+)\b", re.IGNORECASE)


def _build_html_email(subject: str, body: str) -> str:
    escaped = _html.escape(body)
    # Highlight application references like APP-2026-00001
    highlighted = _APP_REF_RE.sub(
        r'<span style="font-family:ui-monospace,monospace;font-weight:600;color:#1d4ed8;">\1</span>',
        escaped,
    )
    paragraphs = "".join(
        f'<p style="margin:0 0 12px 0;line-height:1.65;">{line}</p>'
        if line.strip() else '<p style="margin:0 0 8px 0;">&nbsp;</p>'
        for line in highlighted.splitlines()
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{_html.escape(subject)}</title>
</head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:580px;border-radius:10px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.10);">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#1e3a5f 0%,#1e4d8c 100%);padding:28px 36px 24px;">
              <p style="margin:0;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.55);">Kchekundu Hospital</p>
              <h1 style="margin:6px 0 0;font-size:18px;font-weight:700;color:#ffffff;letter-spacing:-0.01em;">STUD Management System</h1>
              <p style="margin:4px 0 0;font-size:12px;color:rgba(255,255,255,0.60);">Hospital Field &amp; Further Studies Management</p>
            </td>
          </tr>

          <!-- Divider stripe -->
          <tr><td style="height:4px;background:linear-gradient(90deg,#3b82f6,#06b6d4);"></td></tr>

          <!-- Body -->
          <tr>
            <td style="background:#ffffff;padding:32px 36px 28px;">
              <p style="margin:0 0 20px;font-size:13px;font-weight:600;color:#374151;letter-spacing:0.04em;text-transform:uppercase;border-bottom:1px solid #e5e7eb;padding-bottom:10px;">Notification</p>
              <div style="font-size:14px;color:#1f2937;">
                {paragraphs}
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8fafc;border-top:1px solid #e5e7eb;padding:18px 36px;">
              <p style="margin:0;font-size:11px;color:#9ca3af;line-height:1.6;">
                This is an automated message from the STUD Management System. Please do not reply directly to this email.<br>
                &copy; Kchekundu Hospital &mdash; Hospital Field &amp; Further Studies Management System
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _send_email(*, to: str, subject: str, body: str, from_email=None) -> None:
    sender = from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None)
    msg = EmailMultiAlternatives(subject, body, sender, [to])
    msg.attach_alternative(_build_html_email(subject, body), "text/html")
    msg.send(fail_silently=True)


def _maybe_email_copy(*, recipient, subject: str, body: str, force: bool = False) -> None:
    if not force and not getattr(settings, "STUD_EMAIL_NOTIFICATIONS", False):
        return
    email = (getattr(recipient, "email", None) or "").strip()
    if not email:
        return
    try:
        _send_email(to=email, subject=subject, body=body)
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


def send_email_copy(*, recipient, subject: str, body: str, email_override: str = "") -> None:
    """Explicit email channel (independent of in-app notifications).

    Pass email_override to send to a specific address instead of recipient.email
    (e.g. the notification_email the applicant filled in on their application form).
    """
    if email_override.strip():
        if not getattr(settings, "STUD_EMAIL_NOTIFICATIONS", False):
            return
        try:
            _send_email(to=email_override.strip(), subject=subject, body=body)
        except Exception:
            pass
    else:
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


def notify_hod_for_attachment_placement(application) -> None:
    """On HR approval of a student field placement, notify the HOD of the hospital
    department the student is placed in (IT / Nursing / Dentist / Pharmacy …)."""
    dept_id = getattr(application, "hospital_department_id", None)
    if not dept_id:
        return
    ref = application.app_ref or str(application.id)
    assignment_hod_ids = list(
        DepartmentHodAssignment.objects.filter(
            department_id=dept_id, is_active=True
        ).values_list("hod_user_id", flat=True)
    )
    fallback_hod_ids = list(
        HospitalStaff.objects.filter(
            user__role=UserRole.HOD, user__is_active=True, department_id=dept_id
        ).values_list("user_id", flat=True)
    )
    hod_ids = set(assignment_hod_ids + fallback_hod_ids)
    User = get_user_model()
    recipients = list(User.objects.filter(id__in=hod_ids, is_active=True))
    if not recipients:
        return
    notify_users(
        recipients=recipients,
        message=f"Student field placement {ref} was approved by HR and assigned to your department.",
        notif_type=NotificationType.APPROVAL,
        destination_path="/reviewer/field-requests",
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
