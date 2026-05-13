import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.constants import (
    ApplicationStatus,
    ApplicationType,
    PlacementScope,
    ReviewStage,
)


def document_upload_to(instance: "ApplicationDocument", filename: str) -> str:
    now = timezone.now()
    safe = filename.replace("..", "").replace("/", "_")
    return f"documents/{now:%Y/%m}/{safe}"


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    app_ref = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        help_text="Assigned on submit: APP-YYYY-XXXXX",
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    app_type = models.CharField(
        max_length=30,
        choices=ApplicationType.choices,
        default=ApplicationType.FURTHER_STUDIES,
    )
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
    )
    current_stage = models.CharField(max_length=50, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    institution_name = models.CharField(max_length=200, blank=True, default="")
    programme_applied = models.CharField(max_length=200, blank=True, default="")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    sponsorship_type = models.CharField(max_length=100, blank=True, default="")
    reason_for_study = models.TextField(blank=True, default="")
    attachment_dept = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Legacy free-text department; prefer hospital_department when set.",
    )
    hospital_department = models.ForeignKey(
        "hospital_directory.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attachment_requests",
        help_text="Structured hospital department (dropdown).",
    )
    placement_scope = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="individual | group — attachment placement mode.",
    )
    attachment_start = models.DateField(null=True, blank=True)
    attachment_end = models.DateField(null=True, blank=True)
    supervisor_requested = models.CharField(max_length=100, blank=True, default="")
    placement_conducted_site = models.CharField(
        max_length=400,
        blank=True,
        default="",
        help_text="Hospital-confirmed place where field training is conducted (HR / admin).",
    )
    hr_feedback_for_university = models.TextField(
        blank=True,
        default="",
        help_text="HR notes forwarded to university admin with the placement record.",
    )
    field_records_shared_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When placement details were published to the university and student.",
    )

    class Meta:
        db_table = "applications"
        verbose_name = _("study or attachment request")
        verbose_name_plural = _("study & attachment requests")
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status", "current_stage"]),
            models.Index(fields=["applicant", "status"]),
        ]

    def __str__(self) -> str:
        return self.app_ref or str(self.id)

    def clean(self) -> None:
        super().clean()
        terminal = {ApplicationStatus.APPROVED, ApplicationStatus.REJECTED}
        if self.app_type == ApplicationType.FURTHER_STUDIES:
            if self.status in (ApplicationStatus.DRAFT, ApplicationStatus.RETURNED):
                if not self.current_stage:
                    self.current_stage = ReviewStage.HOD
            if self.status not in terminal:
                allowed = {s.value for s in ReviewStage}
                if self.current_stage and self.current_stage not in allowed:
                    raise ValidationError(
                        {"current_stage": "Invalid stage for further studies pipeline."}
                    )
        elif self.app_type == ApplicationType.ATTACHMENT:
            if self.status not in terminal:
                if not self.current_stage:
                    self.current_stage = ReviewStage.HR
                allowed_stages = {ReviewStage.HR}
                if self.current_stage not in allowed_stages:
                    raise ValidationError(
                        {
                            "current_stage": "Attachment requests use the HR review stage until finalized."
                        }
                    )
            if self.placement_scope and self.placement_scope not in {
                PlacementScope.INDIVIDUAL,
                PlacementScope.GROUP,
            }:
                raise ValidationError(
                    {"placement_scope": "Must be 'individual' or 'group'."}
                )


class ApplicationDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    doc_type = models.CharField(max_length=100)
    file = models.FileField(upload_to=document_upload_to, max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "application_documents"
        verbose_name = _("request document")
        verbose_name_plural = _("request documents")
        ordering = ["-uploaded_at"]


class ChangeRequestTarget(models.TextChoices):
    STAFF = "staff", _("Staff member")
    HOD   = "hod",   _("Head of Department")
    BOTH  = "both",  _("Staff and HOD")
    # Internal coordination (same application context; notifications carry application ref)
    TO_ADR = "to_adr", _("Assistant Director (internal — from Top Management)")
    TO_MGMT = "to_mgmt", _("Top Management (internal — from Assistant Director)")


class ChangeRequest(models.Model):
    """Structured log of each change request a reviewer sends on an application."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="change_requests",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="change_requests_sent",
    )
    target = models.CharField(
        max_length=20,
        choices=ChangeRequestTarget.choices,
        default=ChangeRequestTarget.STAFF,
        help_text="Who was notified: staff, hod, both, or internal TM↔ADR coordination.",
    )
    message = models.TextField()
    reply_contact_email = models.EmailField(blank=True, default="")
    notify_via_system = models.BooleanField(default=True)
    notify_via_email = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "application_change_requests"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        ref = self.application.app_ref or str(self.application_id)
        return f"ChangeRequest({ref} → {self.target})"


class ReviewTrail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reviews_given",
    )
    stage = models.CharField(max_length=50)
    decision = models.CharField(max_length=20)
    remarks = models.TextField()
    letter_body = models.TextField(blank=True, default="")
    signature_data = models.TextField(
        blank=True,
        default="",
        help_text="Optional data URL or JSON from reviewer signature capture.",
    )
    feedback_target = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Top Management only: who received this feedback (adr, hod, staff) or empty for final applicant approval.",
    )
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "review_trail"
        verbose_name = _("request review entry")
        verbose_name_plural = _("request review trail")
        ordering = ["-reviewed_at"]
