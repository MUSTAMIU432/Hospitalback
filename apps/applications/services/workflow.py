from __future__ import annotations

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.applications.models import Application, ApplicationDocument, ChangeRequest, ChangeRequestTarget, ReviewTrail
from apps.applications.services import access as access_svc
from apps.employees.models import DepartmentHodAssignment, HospitalStaff
from apps.notifications.models import Notification
from apps.notifications.services import notify
from core.constants import (
    ApplicationStatus,
    ApplicationType,
    NotificationType,
    ReviewDecision,
    ReviewStage,
    StaffCapability,
    UserRole,
)
from apps.employees.services.capabilities import user_has_staff_capability


def _hod_department_ids(user) -> set:
    assigned = set(
        DepartmentHodAssignment.objects.filter(
            hod_user_id=user.id,
            is_active=True,
        ).values_list("department_id", flat=True)
    )
    if assigned:
        return assigned
    own_department_id = getattr(getattr(user, "hospital_staff_profile", None), "department_id", None)
    if own_department_id:
        return {own_department_id}
    profile = HospitalStaff.objects.filter(user_id=user.id).values("department_id").first()
    dep = (profile or {}).get("department_id")
    return {dep} if dep else set()


def _has_target_hod_for_department(department_id) -> bool:
    if DepartmentHodAssignment.objects.filter(department_id=department_id, is_active=True).exists():
        return True
    # Fallback: HOD users whose own staff profile is in the same department.
    return HospitalStaff.objects.filter(
        user__role=UserRole.HOD,
        user__is_active=True,
        department_id=department_id,
    ).exists()


def _next_app_ref() -> str:
    year = timezone.now().year
    prefix = f"APP-{year}-"
    best = 0
    for ref in Application.objects.filter(app_ref__startswith=prefix).values_list(
        "app_ref", flat=True
    ):
        if not ref:
            continue
        try:
            n = int(ref.split("-")[-1])
            best = max(best, n)
        except (TypeError, ValueError):
            continue
    return f"{prefix}{best + 1:05d}"


def _assert_applicant(application: Application, user) -> None:
    if application.applicant_id != user.id:
        raise PermissionDenied("You are not the applicant for this application.")


def _assert_can_review(application: Application, user) -> None:
    role = getattr(user, "role", None)
    stage = application.current_stage
    if application.app_type == ApplicationType.ATTACHMENT:
        if stage != ReviewStage.HR:
            raise PermissionDenied("Application is not at the HR review stage.")
        if role == UserRole.HOSPITAL_ADMIN:
            return
        if role == UserRole.HOSPITAL_STAFF and user_has_staff_capability(
            user, StaffCapability.HR_FIELD_REQUESTS.value
        ):
            return
        raise PermissionDenied(
            "Only HR-designated hospital staff or hospital admin can review attachment requests."
        )
    if stage == ReviewStage.HOD:
        is_hod_reviewer = role == UserRole.HOD or user_has_staff_capability(user, "hod_assess_details")
        if not is_hod_reviewer:
            raise PermissionDenied("Only HOD-assigned reviewers can review at this stage.")
        applicant_department_id = getattr(
            getattr(application.applicant, "hospital_staff_profile", None),
            "department_id",
            None,
        )
        if not applicant_department_id:
            raise PermissionDenied("Applicant department is missing; cannot route HOD review.")
        is_assigned = DepartmentHodAssignment.objects.filter(
            hod_user_id=user.id,
            department_id=applicant_department_id,
            is_active=True,
        ).exists()
        if not is_assigned and applicant_department_id not in _hod_department_ids(user):
            raise PermissionDenied("This application belongs to another department HOD assignment.")
    elif stage == ReviewStage.ASST_DIRECTOR:
        is_adr_reviewer = role == UserRole.ASST_DIRECTOR or user_has_staff_capability(user, "adr_assess_details")
        if not is_adr_reviewer:
            raise PermissionDenied("Only the Assistant Director can review at this stage.")
    elif stage == ReviewStage.MANAGEMENT:
        is_mgmt_reviewer = role == UserRole.MANAGEMENT or user_has_staff_capability(user, "top_review_adr_fb")
        if not is_mgmt_reviewer:
            raise PermissionDenied("Only Management can review at this stage.")
    else:
        raise PermissionDenied("Application is not awaiting review at a known stage.")


@transaction.atomic
def submit_application(*, application: Application, user) -> Application:
    application = Application.objects.select_for_update().get(pk=application.pk)
    _assert_applicant(application, user)
    if application.status not in (
        ApplicationStatus.DRAFT,
        ApplicationStatus.RETURNED,
    ):
        raise ValidationError("Only draft or returned applications can be submitted.")
    application.full_clean()
    application.app_ref = _next_app_ref()
    application.status = ApplicationStatus.SUBMITTED
    application.submitted_at = timezone.now()
    if application.app_type == ApplicationType.FURTHER_STUDIES:
        applicant_department_id = getattr(
            getattr(application.applicant, "hospital_staff_profile", None),
            "department_id",
            None,
        )
        if not applicant_department_id:
            raise ValidationError("Assign a department to this staff profile before submitting.")
        has_target_hod = _has_target_hod_for_department(applicant_department_id)
        if not has_target_hod:
            raise ValidationError(
                "No active HOD assignment exists for your department. Contact hospital admin."
            )
        application.current_stage = ReviewStage.HOD
    else:
        application.current_stage = ReviewStage.HR
    application.save()
    if application.app_type == ApplicationType.FURTHER_STUDIES:
        notify.notify_hod_for_submission(application)
    else:
        notify.notify_hr_for_attachment(application)
    return application


@transaction.atomic
def review_application(
    *,
    application: Application,
    reviewer,
    decision: str,
    remarks: str,
    letter_body: str = "",
    signature_data: str = "",
    request_change_message: str = "",
    feedback_message: str = "",
    feedback_target: str = "",
    notify_via_system: bool = True,
    notify_via_email: bool = False,
) -> Application:
    application = Application.objects.select_for_update().get(pk=application.pk)
    if not remarks or not remarks.strip():
        raise ValidationError("Remarks are required.")
    _assert_can_review(application, reviewer)
    if application.status == ApplicationStatus.RETURNED:
        raise ValidationError(
            "Returned applications must be resubmitted by the applicant before review."
        )
    if application.status not in (
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.UNDER_REVIEW,
    ):
        raise ValidationError("This application is not in a reviewable state.")
    stage = application.current_stage
    ft = (feedback_target or "").strip() if stage == ReviewStage.MANAGEMENT else ""
    ReviewTrail.objects.create(
        application=application,
        reviewer=reviewer,
        stage=stage,
        decision=decision,
        remarks=remarks.strip(),
        letter_body=(letter_body or "").strip(),
        signature_data=(signature_data or "").strip(),
        feedback_target=ft,
    )
    ref = application.app_ref or str(application.id)
    if decision == ReviewDecision.REJECTED:
        application.status = ApplicationStatus.REJECTED
        application.current_stage = ""
        application.save()
        notify.notify_applicant(
            application,
            f"Application {ref} was rejected. Remarks: {remarks.strip()}",
            notif_type=NotificationType.REJECTION,
        )
        return application
    if decision == ReviewDecision.RETURNED:
        application.status = ApplicationStatus.RETURNED
        if application.app_type == ApplicationType.FURTHER_STUDIES:
            application.current_stage = ReviewStage.HOD
        else:
            application.current_stage = ReviewStage.HR
        application.save()
        request_msg = (request_change_message or "").strip()
        payload = (
            f"Application {ref} was returned for revision."
            if not request_msg
            else f"Application {ref} was returned for revision. Message from reviewer: {request_msg}"
        )
        if notify_via_system:
            notify.notify_user(
                recipient=application.applicant,
                message=payload,
                notif_type=NotificationType.REVISION,
                destination_path="/hospital-staff/feedback/changes",
            )
        if notify_via_email:
            notify.send_email_copy(
                recipient=application.applicant,
                subject=f"STUD change request for {ref}",
                body=payload,
            )
        return application
    if decision != ReviewDecision.APPROVED:
        raise ValidationError("Unsupported decision.")
    if application.app_type == ApplicationType.ATTACHMENT:
        if not (application.placement_conducted_site or "").strip():
            raise ValidationError(
                "Set the confirmed field training site before approving (HR placement step)."
            )
        application.status = ApplicationStatus.APPROVED
        application.current_stage = ""
        application.field_records_shared_at = timezone.now()
        application.save()
        notify.notify_applicant(
            application,
            f"Application {ref} was approved. Your field placement is confirmed — download the "
            "acceptance letter from your application when ready.",
            notif_type=NotificationType.APPROVAL,
        )
        notify.notify_univ_admins_field_placement(application)
        return application
    if stage == ReviewStage.HOD:
        application.status = ApplicationStatus.UNDER_REVIEW
        application.current_stage = ReviewStage.ASST_DIRECTOR
        application.save()
        custom = (feedback_message or "").strip()
        sender_name = _sender_display_name(reviewer)
        msg = (
            f"Application {ref} forwarded to Assistant Director by {sender_name}."
            if not custom
            else f"Application {ref} forwarded by {sender_name}. Message: {custom}"
        )
        if notify_via_system:
            notify.notify_asst_directors_for_application(application, message=msg)
        if notify_via_email:
            for recipient in notify._asst_director_recipients():
                notify.send_email_copy(
                    recipient=recipient,
                    subject=f"STUD review forwarded — {ref}",
                    body=msg,
                )
    elif stage == ReviewStage.ASST_DIRECTOR:
        application.status = ApplicationStatus.UNDER_REVIEW
        application.current_stage = ReviewStage.MANAGEMENT
        application.save()
        custom = (feedback_message or "").strip()
        sender_name = _sender_display_name(reviewer)
        msg = (
            f"Application {ref} forwarded to Management by {sender_name}."
            if not custom
            else f"Application {ref} forwarded by {sender_name}. Message: {custom}"
        )
        if notify_via_system:
            notify.notify_management_for_application(application, message=msg)
        if notify_via_email:
            for recipient in notify._management_recipients():
                notify.send_email_copy(
                    recipient=recipient,
                    subject=f"STUD review forwarded — {ref}",
                    body=msg,
                )
    elif stage == ReviewStage.MANAGEMENT:
        _handle_management_review(
            application=application,
            reviewer=reviewer,
            ref=ref,
            feedback_message=feedback_message,
            feedback_target=feedback_target,
            notify_via_system=notify_via_system,
            notify_via_email=notify_via_email,
        )
    else:
        raise ValidationError("Invalid pipeline stage.")
    return application


def _handle_management_review(
    *,
    application: Application,
    reviewer,
    ref: str,
    feedback_message: str,
    feedback_target: str,
    notify_via_system: bool,
    notify_via_email: bool,
) -> None:
    """
    Management-stage review dispatch.

    feedback_target controls who receives this review:
      ""       → final decision: applicant is notified, application approved
      "adr"    → feedback forwarded to Assistant Director (stage stays management)
      "hod"    → feedback forwarded to Head of Department (stage stays management)
      "staff"  → feedback sent directly to staff applicant (stage stays management)
    """
    sender_name = _sender_display_name(reviewer)
    custom = (feedback_message or "").strip()

    if feedback_target == "adr":
        # Forward to ADR — application stays at management stage pending ADR action
        msg = (
            f"Top Management review feedback on {ref} — forwarded to you by {sender_name}."
            if not custom
            else f"Top Management review feedback on {ref} from {sender_name}: {custom}"
        )
        if notify_via_system:
            notify.notify_asst_directors_for_application(application, message=msg)
        if notify_via_email:
            for recipient in notify._asst_director_recipients():
                notify.send_email_copy(
                    recipient=recipient,
                    subject=f"STUD management feedback — {ref}",
                    body=msg,
                )

    elif feedback_target == "hod":
        # Forward to HOD — application stays at management stage
        msg = (
            f"Top Management review feedback on {ref} — forwarded to you by {sender_name}."
            if not custom
            else f"Top Management review feedback on {ref} from {sender_name}: {custom}"
        )
        hod_recipients = notify._hod_recipients_for_application(application)
        if notify_via_system:
            notify.notify_users(
                recipients=hod_recipients,
                message=msg,
                notif_type=NotificationType.REVISION,
            )
        if notify_via_email:
            for hod in hod_recipients:
                notify.send_email_copy(
                    recipient=hod,
                    subject=f"STUD management feedback — {ref}",
                    body=msg,
                )

    elif feedback_target == "staff":
        # Notify the staff applicant directly (informational, no stage change)
        msg = (
            f"Review feedback from Top Management on application {ref}."
            if not custom
            else f"Review feedback from Top Management on {ref}: {custom}"
        )
        if notify_via_system:
            notify.notify_applicant(application, msg, notif_type=NotificationType.REVISION)
        if notify_via_email:
            notify.send_email_copy(
                recipient=application.applicant,
                subject=f"STUD review feedback — {ref}",
                body=msg,
            )

    else:
        # Final approval — default path
        application.status = ApplicationStatus.APPROVED
        application.current_stage = ""
        application.save()
        approval_msg = custom or f"Application {ref} was approved by Top Management."
        if notify_via_system:
            notify.notify_applicant(
                application,
                approval_msg,
                notif_type=NotificationType.APPROVAL,
            )
        if notify_via_email:
            notify.send_email_copy(
                recipient=application.applicant,
                subject=f"STUD final decision — {ref}",
                body=approval_msg,
            )


REVIEW_FEEDBACK_LETTER_DOC_TYPE = "review_feedback_letter"
REVIEW_FEEDBACK_LETTER_MAX_BYTES = 12 * 1024 * 1024


def render_review_feedback_letter_template_html(
    application: Application, *, signer_placeholder: str = ""
) -> str:
    """Render the official HTML letter shell (Django template) for reviewer download / editor import."""
    from django.template.loader import render_to_string

    apl = application.applicant
    parts = [getattr(apl, "first_name", None) or "", getattr(apl, "last_name", None) or ""]
    applicant_name = " ".join(p for p in parts if p).strip()
    if not applicant_name and hasattr(apl, "get_full_name"):
        applicant_name = (apl.get_full_name() or "").strip()
    if not applicant_name:
        applicant_name = getattr(apl, "username", "") or "Applicant"
    ph = (signer_placeholder or "").strip() or "[Your Name]"
    return render_to_string(
        "applications/review_feedback_letter.html",
        {
            "app_ref": application.app_ref or "",
            "applicant_name": applicant_name,
            "institution_name": application.institution_name or "",
            "programme_applied": application.programme_applied or "",
            "signer_placeholder": ph,
        },
    )


def can_reviewer_upload_feedback_letter(user, application: Application) -> bool:
    """Reviewers may attach a formal letter file while preparing feedback (stored as ApplicationDocument)."""
    if not access_svc.can_view_application(user, application):
        return False
    if application.app_type != ApplicationType.FURTHER_STUDIES:
        return False
    return True


def assert_can_download_review_feedback_document(user, document: ApplicationDocument) -> None:
    assert_can_view(user, document.application)
    if document.doc_type != REVIEW_FEEDBACK_LETTER_DOC_TYPE:
        raise PermissionDenied("This document is not a review feedback letter.")


def assert_can_view(user, application: Application) -> None:
    if not access_svc.can_view_application(user, application):
        raise PermissionDenied("You cannot access this application.")


def _sender_display_name(sender) -> str:
    """Human-readable name + position for notification messages."""
    from apps.users.graphql.types import UserType
    full_name = " ".join(
        p for p in [getattr(sender, "first_name", ""), getattr(sender, "last_name", "")] if p
    ).strip() or getattr(sender, "username", "Reviewer")
    position = UserType.profile_title(None, sender)
    return f"{full_name} ({position})"


def _can_send_change_request_to_hod(sender) -> bool:
    """ADR and Top Management can explicitly address the HOD."""
    role = getattr(sender, "role", "")
    return (
        role in (UserRole.ASST_DIRECTOR, UserRole.MANAGEMENT)
        or user_has_staff_capability(sender, "adr_assess_details")
        or user_has_staff_capability(sender, "top_assess_details")
    )


def _can_send_internal_to_adr(sender) -> bool:
    """Top Management may send internal coordination messages to Assistant Director(s)."""
    role = getattr(sender, "role", "")
    return role == UserRole.MANAGEMENT or user_has_staff_capability(sender, "top_assess_details")


def _can_send_internal_to_mgmt(sender) -> bool:
    """Assistant Director may send internal coordination messages to Top Management."""
    role = getattr(sender, "role", "")
    return role == UserRole.ASST_DIRECTOR or user_has_staff_capability(sender, "adr_assess_details")


def user_can_see_internal_change_requests(user) -> bool:
    """Who may see TM↔ADR internal coordination rows on an application."""
    if user is None or not getattr(user, "is_authenticated", True):
        return False
    role = getattr(user, "role", "")
    if role in (UserRole.MANAGEMENT, UserRole.ASST_DIRECTOR):
        return True
    return user_has_staff_capability(user, "adr_assess_details") or user_has_staff_capability(
        user, "top_assess_details"
    )


def send_application_change_request(
    *,
    application: Application,
    sender,
    message: str,
    target: str = ChangeRequestTarget.STAFF,
    notify_via_system: bool = True,
    notify_via_email: bool = False,
    reply_contact_email: str = "",
) -> Application:
    """
    Reviewer sends a change request to the staff applicant and/or the HOD.

    ``target`` controls who is notified:
      - "staff"  → only the applicant (default; all reviewers)
      - "hod"    → only the HOD for the applicant's department (ADR / Top Mgmt only)
      - "both"   → staff AND HOD (ADR / Top Mgmt only)

    HOD can only send to "staff".
    """
    assert_can_view(sender, application)
    if application.applicant_id == sender.id:
        raise PermissionDenied("You cannot send a change request on your own application.")
    if application.app_type != ApplicationType.FURTHER_STUDIES:
        raise ValidationError("Change requests are only supported for further-studies applications.")
    if application.status not in (
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.RETURNED,
    ):
        raise ValidationError("This application is not open for change requests at this time.")
    body = (message or "").strip()
    if not body:
        raise ValidationError("Change request description is required.")
    if not notify_via_system and not notify_via_email:
        raise ValidationError("Select at least one delivery channel (system or email).")

    valid_targets = {
        ChangeRequestTarget.STAFF,
        ChangeRequestTarget.HOD,
        ChangeRequestTarget.BOTH,
        ChangeRequestTarget.TO_ADR,
        ChangeRequestTarget.TO_MGMT,
    }
    if target not in valid_targets:
        target = ChangeRequestTarget.STAFF

    # ── Internal Top Management ↔ Assistant Director (in-app notifications + ADR workspace) ──
    internal_targets = frozenset({ChangeRequestTarget.TO_ADR, ChangeRequestTarget.TO_MGMT})
    if target in internal_targets:
        adr_workspace = f"/hospital-staff/adr-change-requests/{application.id}"
        if target == ChangeRequestTarget.TO_ADR:
            if not _can_send_internal_to_adr(sender):
                raise PermissionDenied(
                    "Only Top Management can send internal coordination requests to the Assistant Director."
                )
            recipients = notify._asst_director_recipients()
            title_line = f"Application {ref} — Top Management → Assistant Director"
        else:
            if not _can_send_internal_to_mgmt(sender):
                raise PermissionDenied(
                    "Only the Assistant Director can send internal coordination requests to Top Management."
                )
            recipients = notify._management_recipients()
            title_line = f"Application {ref} — Assistant Director → Top Management"

        payload = f"{title_line}\nFrom: {sender_name}\n\n{body}"
        for user_r in recipients:
            if user_r.id == sender.id:
                continue
            if notify_via_system:
                Notification.objects.create(
                    recipient=user_r,
                    sender=sender,
                    message=payload,
                    notif_type=NotificationType.REVISION,
                    destination_path=adr_workspace,
                )
            if notify_via_email:
                notify.send_email_copy(
                    recipient=user_r,
                    subject=f"STUD {title_line} — {ref}",
                    body=payload,
                )

        ChangeRequest.objects.create(
            application=application,
            sender=sender,
            target=target,
            message=body,
            reply_contact_email=reply,
            notify_via_system=notify_via_system,
            notify_via_email=notify_via_email,
        )
        return application

    # Only ADR / Top Mgmt may address the HOD directly
    if target in (ChangeRequestTarget.HOD, ChangeRequestTarget.BOTH):
        if not _can_send_change_request_to_hod(sender):
            raise PermissionDenied(
                "Only Assistant Director or Top Management can send change requests directly to the Head of Department."
            )

    ref = application.app_ref or str(application.id)
    reply = (reply_contact_email or "").strip()
    sender_name = _sender_display_name(sender)

    notify_staff = target in (ChangeRequestTarget.STAFF, ChangeRequestTarget.BOTH)
    notify_hod   = target in (ChangeRequestTarget.HOD, ChangeRequestTarget.BOTH)

    # ── Staff notification ────────────────────────────────────────────────────
    if notify_staff:
        applicant_lines = [
            f"Application {ref} — change request (staff applicant)",
            f"From: {sender_name}",
            "",
            body,
        ]
        if reply:
            applicant_lines.extend(["", f"You may reply to: {reply}"])
        applicant_payload = "\n".join(applicant_lines)

        if notify_via_system:
            Notification.objects.create(
                recipient=application.applicant,
                sender=sender,
                message=applicant_payload,
                notif_type=NotificationType.REVISION,
                destination_path="/hospital-staff/feedback/changes",
            )
        if notify_via_email:
            notify.send_email_copy(
                recipient=application.applicant,
                subject=f"STUD change request — {ref}",
                body=applicant_payload,
            )

    # ── HOD notification ──────────────────────────────────────────────────────
    if notify_hod:
        hod_lines = [
            (
                f"Application {ref} — [CC] change request (Head of Department)"
                if notify_staff
                else f"Application {ref} — change request (Head of Department)"
            ),
            f"Issued by: {sender_name}",
            f"Applicant: {application.applicant.get_full_name() or application.applicant.username}",
            "",
            body,
        ]
        if reply:
            hod_lines.extend(["", f"Reviewer contact: {reply}"])
        hod_payload = "\n".join(hod_lines)

        hod_recipients = notify._hod_recipients_for_application(application)
        for hod_user in hod_recipients:
            if hod_user.id != sender.id:
                if notify_via_system:
                    Notification.objects.create(
                        recipient=hod_user,
                        sender=sender,
                        message=hod_payload,
                        notif_type=NotificationType.REVISION,
                        destination_path=f"/hospital-staff/adr-change-requests/{application.id}",
                    )
                if notify_via_email:
                    notify.send_email_copy(
                        recipient=hod_user,
                        subject=f"STUD change request (CC) — {ref}",
                        body=hod_payload,
                    )

    # ── Structured log ────────────────────────────────────────────────────────
    ChangeRequest.objects.create(
        application=application,
        sender=sender,
        target=target,
        message=body,
        reply_contact_email=reply,
        notify_via_system=notify_via_system,
        notify_via_email=notify_via_email,
    )

    return application


def _assert_can_hr_edit_attachment(application: Application, user) -> None:
    if application.app_type != ApplicationType.ATTACHMENT:
        raise PermissionDenied("Not a field attachment request.")
    if application.current_stage != ReviewStage.HR:
        raise PermissionDenied("Placement can only be edited while the request is with HR.")
    if application.status not in (
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.RETURNED,
    ):
        raise PermissionDenied("This request is not open for HR edits.")
    role = getattr(user, "role", None)
    if role == UserRole.HOSPITAL_ADMIN:
        return
    if role == UserRole.HOSPITAL_STAFF and user_has_staff_capability(
        user, StaffCapability.HR_FIELD_REQUESTS.value
    ):
        return
    raise PermissionDenied("Only HR-designated staff or hospital admin can update placement details.")


@transaction.atomic
def set_attachment_placement_fields(
    *,
    application: Application,
    editor,
    placement_conducted_site: str | None = None,
    hr_feedback_for_university: str | None = None,
) -> Application:
    application = Application.objects.select_for_update().get(pk=application.pk)
    _assert_can_hr_edit_attachment(application, editor)
    if placement_conducted_site is not None:
        application.placement_conducted_site = placement_conducted_site.strip()
    if hr_feedback_for_university is not None:
        application.hr_feedback_for_university = hr_feedback_for_university.strip()
    application.save(update_fields=["placement_conducted_site", "hr_feedback_for_university"])
    return application


def can_hr_upload_attachment_document(user, application: Application) -> bool:
    try:
        _assert_can_hr_edit_attachment(application, user)
        return True
    except PermissionDenied:
        return False


@transaction.atomic
def mark_application_opened(*, application: Application, reviewer) -> Application:
    """
    Transitions a submitted application to under_review when a reviewer first opens it.
    Stage does not change — only status moves from submitted → under_review.
    No-op if already under_review or in any other state.
    """
    application = Application.objects.select_for_update().get(pk=application.pk)
    if application.status != ApplicationStatus.SUBMITTED:
        return application
    try:
        _assert_can_review(application, reviewer)
    except PermissionDenied:
        return application
    application.status = ApplicationStatus.UNDER_REVIEW
    application.save(update_fields=["status", "updated_at"])
    return application


@transaction.atomic
def withdraw_application(*, application: Application, user) -> Application:
    application = Application.objects.select_for_update().get(pk=application.pk)
    _assert_applicant(application, user)
    if application.status not in (
        ApplicationStatus.DRAFT,
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.RETURNED,
    ):
        raise ValidationError("This application cannot be withdrawn.")
    application.status = ApplicationStatus.RETURNED
    if application.app_type == ApplicationType.FURTHER_STUDIES:
        application.current_stage = ReviewStage.HOD
    else:
        application.current_stage = ReviewStage.HR
    application.save(update_fields=["status", "current_stage", "updated_at"])
    return application


@transaction.atomic
def archive_application(*, application: Application, user) -> None:
    application = Application.objects.select_for_update().get(pk=application.pk)
    _assert_applicant(application, user)
    if application.status in (ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW):
        raise ValidationError("Withdraw this application before archiving.")
    application.delete()


@transaction.atomic
def reopen_application_for_resubmission(*, application: Application, user) -> Application:
    """
    Applicant reopens a final decision (approved/rejected) back to returned,
    allowing edits and a fresh submission cycle.
    """
    application = Application.objects.select_for_update().get(pk=application.pk)
    _assert_applicant(application, user)
    if application.status not in (ApplicationStatus.APPROVED, ApplicationStatus.REJECTED):
        raise ValidationError("Only finalised applications can be reopened for resubmission.")
    application.status = ApplicationStatus.RETURNED
    if application.app_type == ApplicationType.FURTHER_STUDIES:
        application.current_stage = ReviewStage.HOD
    else:
        application.current_stage = ReviewStage.HR
    application.save(update_fields=["status", "current_stage", "updated_at"])
    return application
