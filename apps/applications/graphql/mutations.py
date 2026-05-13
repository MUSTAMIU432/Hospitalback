import base64
import uuid

import strawberry
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from strawberry.types import Info

from apps.applications.graphql.inputs import ApplicationDraftInput, ApplicationUpdateInput
from apps.applications.graphql.types import (
    ApplicationDocumentType,
    ApplicationType,
    PdfPayload,
)
from apps.applications.models import Application
from apps.applications.services import workflow
from apps.applications.services.field_acceptance_pdf import build_field_acceptance_pdf
from apps.users.graphql.auth import require_auth
from apps.users.graphql.types import OperationResult
from core.constants import (
    ApplicationStatus,
    ApplicationType as ApplicationTypeEnum,
    PlacementScope,
    ReviewDecision,
    UserRole,
)


@strawberry.type
class StudyRequestsMutation:
    @strawberry.mutation
    def create_draft_application(
        self, info: Info, data: ApplicationDraftInput
    ) -> ApplicationType:
        user = require_auth(info)
        app_type = data.app_type
        if app_type not in {
            ApplicationTypeEnum.FURTHER_STUDIES,
            ApplicationTypeEnum.ATTACHMENT,
        }:
            raise ValidationError("Invalid application type.")
        _FURTHER_STUDIES_CREATORS = {
            UserRole.HOSPITAL_STAFF,
            UserRole.HOD,
            UserRole.ASST_DIRECTOR,
            UserRole.MANAGEMENT,
        }
        if app_type == ApplicationTypeEnum.FURTHER_STUDIES and user.role not in _FURTHER_STUDIES_CREATORS:
            raise PermissionDenied("Only hospital staff and reviewer roles can create further-studies applications.")
        if app_type == ApplicationTypeEnum.ATTACHMENT and user.role != UserRole.STUDENT:
            raise PermissionDenied("Only students can create attachment applications.")
        app = Application(
            applicant=user,
            app_type=app_type,
            status=ApplicationStatus.DRAFT,
        )
        app.full_clean()
        app.save()
        return app

    @strawberry.mutation
    def update_my_application(
        self,
        info: Info,
        application_id: uuid.UUID,
        data: ApplicationUpdateInput,
    ) -> ApplicationType:
        user = require_auth(info)
        app = Application.objects.get(pk=application_id)
        if app.applicant_id != user.id:
            raise PermissionDenied("Not your application.")
        if app.status not in (ApplicationStatus.DRAFT, ApplicationStatus.RETURNED):
            raise ValidationError("Only draft or returned applications can be edited.")
        fields = [
            "institution_name",
            "programme_applied",
            "start_date",
            "end_date",
            "sponsorship_type",
            "reason_for_study",
            "attachment_dept",
            "attachment_start",
            "attachment_end",
            "supervisor_requested",
        ]
        payload = {
            "institution_name": data.institution_name,
            "programme_applied": data.programme_applied,
            "start_date": data.start_date,
            "end_date": data.end_date,
            "sponsorship_type": data.sponsorship_type,
            "reason_for_study": data.reason_for_study,
            "attachment_dept": data.attachment_dept,
            "attachment_start": data.attachment_start,
            "attachment_end": data.attachment_end,
            "supervisor_requested": data.supervisor_requested,
        }
        for name in fields:
            val = payload[name]
            if val is not None:
                setattr(app, name, val)
        if data.placement_scope is not None:
            ps = data.placement_scope.strip()
            allowed = {PlacementScope.INDIVIDUAL, PlacementScope.GROUP}
            if ps and ps not in allowed:
                raise ValidationError("placement_scope must be individual or group.")
            app.placement_scope = ps
        if data.hospital_department_id is not None:
            from apps.hospital_directory.models import Department

            try:
                app.hospital_department = Department.objects.get(
                    pk=data.hospital_department_id
                )
            except Department.DoesNotExist as exc:
                raise ValidationError("Hospital department not found.") from exc
        app.full_clean()
        app.save()
        return app

    @strawberry.mutation
    def submit_my_application(self, info: Info, application_id: uuid.UUID) -> ApplicationType:
        user = require_auth(info)
        app = Application.objects.get(pk=application_id)
        workflow.submit_application(application=app, user=user)
        return Application.objects.get(pk=application_id)

    @strawberry.mutation
    def withdraw_my_application(self, info: Info, application_id: uuid.UUID) -> ApplicationType:
        user = require_auth(info)
        app = Application.objects.get(pk=application_id)
        workflow.withdraw_application(application=app, user=user)
        return Application.objects.get(pk=application_id)

    @strawberry.mutation
    def archive_my_application(self, info: Info, application_id: uuid.UUID) -> OperationResult:
        user = require_auth(info)
        app = Application.objects.get(pk=application_id)
        workflow.archive_application(application=app, user=user)
        return OperationResult(ok=True, message="Application archived.")

    @strawberry.mutation
    def reopen_my_application_for_resubmission(self, info: Info, application_id: uuid.UUID) -> ApplicationType:
        user = require_auth(info)
        app = Application.objects.get(pk=application_id)
        workflow.reopen_application_for_resubmission(application=app, user=user)
        return Application.objects.get(pk=application_id)

    @strawberry.mutation
    def mark_application_opened(self, info: Info, application_id: uuid.UUID) -> ApplicationType:
        """Reviewer opens an application — transitions submitted → under_review (same stage)."""
        reviewer = require_auth(info)
        app = Application.objects.get(pk=application_id)
        workflow.mark_application_opened(application=app, reviewer=reviewer)
        return Application.objects.get(pk=application_id)

    @strawberry.mutation
    def send_application_change_request(
        self,
        info: Info,
        application_id: uuid.UUID,
        message: str,
        target: str = "staff",
        notify_via_system: bool = True,
        notify_via_email: bool = False,
        reply_contact_email: str = "",
    ) -> ApplicationType:
        """Send a change request to the staff applicant and/or HOD. Does not change application status."""
        sender = require_auth(info)
        app = Application.objects.get(pk=application_id)
        workflow.send_application_change_request(
            application=app,
            sender=sender,
            message=message,
            target=target,
            notify_via_system=notify_via_system,
            notify_via_email=notify_via_email,
            reply_contact_email=reply_contact_email,
        )
        return Application.objects.get(pk=application_id)

    @strawberry.mutation
    def review_application(
        self,
        info: Info,
        application_id: uuid.UUID,
        decision: str,
        remarks: str,
        letter_body: str = "",
        signature_data: str = "",
        request_change_message: str = "",
        feedback_message: str = "",
        feedback_target: str = "",
        notify_via_system: bool = True,
        notify_via_email: bool = False,
    ) -> ApplicationType:
        reviewer = require_auth(info)
        app = Application.objects.get(pk=application_id)
        if decision not in {
            ReviewDecision.APPROVED,
            ReviewDecision.REJECTED,
            ReviewDecision.RETURNED,
        }:
            raise ValidationError("Invalid decision.")
        workflow.review_application(
            application=app,
            reviewer=reviewer,
            decision=decision,
            remarks=remarks,
            letter_body=letter_body,
            signature_data=signature_data,
            request_change_message=request_change_message,
            feedback_message=feedback_message,
            feedback_target=feedback_target,
            notify_via_system=notify_via_system,
            notify_via_email=notify_via_email,
        )
        return Application.objects.get(pk=application_id)

    @strawberry.mutation
    def add_application_document(
        self,
        info: Info,
        application_id: uuid.UUID,
        doc_type: str,
        filename: str,
        file_base64: str,
    ) -> ApplicationDocumentType:
        from apps.applications.models import ApplicationDocument

        user = require_auth(info)
        app = Application.objects.get(pk=application_id)
        if app.applicant_id == user.id:
            if app.status not in (ApplicationStatus.DRAFT, ApplicationStatus.RETURNED):
                raise ValidationError("Documents can only be added while drafting or revising.")
            if doc_type == workflow.REVIEW_FEEDBACK_LETTER_DOC_TYPE:
                raise PermissionDenied("This document type is reserved for reviewer letter uploads.")
        elif doc_type == workflow.REVIEW_FEEDBACK_LETTER_DOC_TYPE and workflow.can_reviewer_upload_feedback_letter(
            user, app
        ):
            pass
        elif workflow.can_hr_upload_attachment_document(user, app):
            pass
        else:
            raise PermissionDenied("Not allowed to upload documents for this application.")
        raw = base64.b64decode(file_base64)
        if doc_type == workflow.REVIEW_FEEDBACK_LETTER_DOC_TYPE and len(raw) > workflow.REVIEW_FEEDBACK_LETTER_MAX_BYTES:
            raise ValidationError("Review feedback letter exceeds the maximum allowed size.")
        doc = ApplicationDocument(application=app, doc_type=doc_type)
        doc.file.save(filename, ContentFile(raw), save=True)
        return doc

    @strawberry.mutation
    def delete_change_request(self, info: Info, request_id: uuid.UUID) -> OperationResult:
        """Delete a change request. Only the sender or ADR/management may delete."""
        from apps.applications.models import ChangeRequest

        user = require_auth(info)
        cr = ChangeRequest.objects.select_related("application").get(pk=request_id)
        allowed_roles = {UserRole.ASST_DIRECTOR, UserRole.MANAGEMENT}
        if cr.sender_id != user.id and getattr(user, "role", None) not in allowed_roles:
            raise PermissionDenied("You can only delete change requests you sent.")
        cr.delete()
        return OperationResult(ok=True, message="Change request deleted.")

    @strawberry.mutation
    def forward_final_letter_to_hod(self, info: Info, application_ids: list[uuid.UUID]) -> OperationResult:
        """ADR notifies HOD(s) that Top Management final letters are ready."""
        from apps.applications.models import Application, ReviewTrail
        from apps.employees.models import DepartmentHodAssignment, HospitalStaff
        from apps.notifications.models import Notification

        user = require_auth(info)
        if getattr(user, "role", None) != UserRole.ASST_DIRECTOR:
            raise PermissionDenied("Only the Assistant Director can forward final letters to HOD.")

        sender_name = " ".join(filter(None, [user.first_name, user.last_name])) or user.username
        forwarded = 0
        for app_id in application_ids:
            app = Application.objects.select_related("applicant").get(pk=app_id)
            # Require at least one management review on this application
            if not ReviewTrail.objects.filter(application=app, stage="management").exists():
                continue
            ref = app.app_ref or str(app.id)
            # Resolve HOD recipients from applicant's department
            applicant_staff = HospitalStaff.objects.filter(user_id=app.applicant_id).first()
            department_id = getattr(applicant_staff, "department_id", None)
            hod_users = []
            if department_id:
                assignments = DepartmentHodAssignment.objects.filter(
                    department_id=department_id, is_active=True
                ).select_related("hod_user")
                hod_users = [a.hod_user for a in assignments]
                if not hod_users:
                    hod_staff = HospitalStaff.objects.filter(
                        department_id=department_id,
                        user__role=UserRole.HOD,
                    ).select_related("user")
                    hod_users = [s.user for s in hod_staff]
            for hod_user in hod_users:
                Notification.objects.create(
                    recipient=hod_user,
                    sender=user,
                    message=(
                        f"Application {ref} — Final Decision Ready\n"
                        f"Forwarded by: {sender_name} (Assistant Director)\n\n"
                        "Top Management has issued the final decision for this application. "
                        "Please review the final application report."
                    ),
                    notif_type=NotificationType.APPROVAL,
                    destination_path="/reviewer/final-letter",
                )
            forwarded += 1
        return OperationResult(ok=True, message=f"Final letter forwarded for {forwarded} application(s).")

    @strawberry.mutation
    def delete_review_trail_entry(self, info: Info, review_id: uuid.UUID) -> OperationResult:
        """Delete a ReviewTrail record. Restricted to management role only."""
        from apps.applications.models import ReviewTrail

        user = require_auth(info)
        if getattr(user, "role", None) != UserRole.MANAGEMENT:
            raise PermissionDenied("Only top management may delete review trail entries.")
        entry = ReviewTrail.objects.select_related("application").get(pk=review_id)
        entry.delete()
        return OperationResult(ok=True, message="Review trail entry deleted.")

    @strawberry.mutation
    def delete_application_document(self, info: Info, document_id: uuid.UUID) -> OperationResult:
        from apps.applications.models import ApplicationDocument

        user = require_auth(info)
        doc = ApplicationDocument.objects.select_related("application").get(pk=document_id)
        app = doc.application
        if app.applicant_id == user.id:
            if app.status not in (ApplicationStatus.DRAFT, ApplicationStatus.RETURNED):
                raise ValidationError("Documents can only be removed while drafting or revising.")
            if doc.doc_type == workflow.REVIEW_FEEDBACK_LETTER_DOC_TYPE:
                raise PermissionDenied("This document type is reserved for reviewer feedback workspace.")
        elif workflow.can_hr_upload_attachment_document(user, app):
            pass
        elif doc.doc_type == workflow.REVIEW_FEEDBACK_LETTER_DOC_TYPE and workflow.can_reviewer_upload_feedback_letter(
            user, app
        ):
            pass
        else:
            raise PermissionDenied("Not allowed to remove this document.")

        if doc.file:
            doc.file.delete(save=False)
        doc.delete()
        return OperationResult(ok=True, message="Document deleted.")

    @strawberry.mutation
    def set_attachment_placement_fields(
        self,
        info: Info,
        application_id: uuid.UUID,
        placement_conducted_site: str | None = None,
        hr_feedback_for_university: str | None = None,
    ) -> ApplicationType:
        editor = require_auth(info)
        app = Application.objects.get(pk=application_id)
        workflow.set_attachment_placement_fields(
            application=app,
            editor=editor,
            placement_conducted_site=placement_conducted_site,
            hr_feedback_for_university=hr_feedback_for_university,
        )
        return Application.objects.get(pk=application_id)

    @strawberry.mutation
    def field_acceptance_pdf_base64(self, info: Info, application_id: uuid.UUID) -> PdfPayload:
        user = require_auth(info)
        if getattr(user, "role", None) != UserRole.STUDENT:
            raise PermissionDenied("Only students may download the field acceptance letter.")
        app = Application.objects.get(pk=application_id)
        if app.applicant_id != user.id:
            raise PermissionDenied("Not your application.")
        try:
            raw = build_field_acceptance_pdf(app)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        ref = (app.app_ref or str(app.id)).replace("/", "-")
        return PdfPayload(
            filename=f"field-acceptance-{ref}.pdf",
            content_base64=base64.b64encode(raw).decode("ascii"),
        )


# Backwards-compatible names for imports / docs
ApplicationsMutation = StudyRequestsMutation
