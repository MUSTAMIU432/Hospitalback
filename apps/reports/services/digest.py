from django.db.models import Count

from apps.applications.models import Application
from apps.employees.models import HospitalStaff
from apps.imports.models import ImportBatch
from apps.notifications.models import Notification
from apps.students.models import StudentProfile
from apps.users.models import User
from core.constants import ApplicationType, ImportBatchType, UserRole


def dashboard_digest_for_user(user) -> dict:
    """Role-aware counts for admin / superadmin dashboards."""
    role = getattr(user, "role", None)
    out: dict = {
        "applications_total": 0,
        "applications_by_status": [],
        "hospital_staff_total": 0,
        "students_total": 0,
        "users_total": 0,
        "unread_notifications": 0,
        "recent_import_batches": 0,
    }
    if not user.is_authenticated:
        return out

    out["unread_notifications"] = Notification.objects.filter(
        recipient=user, is_read=False
    ).count()

    if role == UserRole.SYSADMIN:
        out["users_total"] = User.objects.filter(
            role__in=(UserRole.HOSPITAL_ADMIN, UserRole.UNIV_ADMIN)
        ).count()
        return out

    if role == UserRole.HOSPITAL_ADMIN:
        out["hospital_staff_total"] = HospitalStaff.objects.count()
        out["recent_import_batches"] = ImportBatch.objects.filter(
            batch_type=ImportBatchType.HOSPITAL_STAFF
        ).count()
    elif role == UserRole.UNIV_ADMIN:
        out["students_total"] = StudentProfile.objects.count()
        out["recent_import_batches"] = ImportBatch.objects.filter(
            batch_type=ImportBatchType.STUDENT
        ).count()

    app_qs = Application.objects.all()
    if role == UserRole.HOSPITAL_STAFF:
        app_qs = app_qs.filter(applicant=user)
    elif role == UserRole.STUDENT:
        app_qs = app_qs.filter(applicant=user)
    elif role == UserRole.HOD:
        app_qs = app_qs.filter(applicant__hospital_staff_profile__hod=user)
    elif role == UserRole.UNIV_ADMIN:
        app_qs = app_qs.filter(app_type=ApplicationType.ATTACHMENT)
    elif role == UserRole.HOSPITAL_ADMIN:
        pass
    elif role not in (UserRole.MANAGEMENT, UserRole.ASST_DIRECTOR):
        app_qs = Application.objects.none()

    out["applications_total"] = app_qs.count()
    by_status = (
        app_qs.values("status")
        .annotate(c=Count("id"))
        .order_by("status")
    )
    out["applications_by_status"] = list(by_status)
    return out
