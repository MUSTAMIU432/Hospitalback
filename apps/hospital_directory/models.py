import uuid

from django.db import models


class Department(models.Model):
    """Hospital department (dropdown + HR structure)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, blank=True, default="")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hospital_departments"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class Designation(models.Model):
    """Job title / cadre (dropdown)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hospital_designations"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class WorkingSite(models.Model):
    """Physical work location (dropdown)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hospital_working_sites"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class SponsorshipType(models.Model):
    """Further-studies sponsorship options (hospital admin maintained)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hospital_sponsorship_types"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class ApplicationDocumentKind(models.Model):
    """
    Allowed values for application document uploads (`ApplicationDocument.doc_type`).
    Code is stored on the document row; label is shown in UI.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=80, unique=True)
    label = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hospital_application_document_kinds"
        ordering = ["sort_order", "code"]

    def __str__(self) -> str:
        return f"{self.code} — {self.label}"
