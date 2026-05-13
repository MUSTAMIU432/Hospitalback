import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class StaffRole(models.Model):
    """Database-driven role catalog for hospital staff."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(
        max_length=60,
        unique=True,
        validators=[RegexValidator(r"^[a-z0-9_\.]+$", "Use lowercase code, e.g. hod or training_manager.")],
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "staff_roles"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class StaffCapability(models.Model):
    """Database-driven permissions catalog."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(
        max_length=80,
        unique=True,
        validators=[RegexValidator(r"^[a-z0-9_\.]+$", "Use lowercase capability code.")],
    )
    label = models.CharField(max_length=180)
    description = models.TextField(blank=True, default="")
    module = models.CharField(max_length=80, blank=True, default="general")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "staff_capabilities_catalog"
        ordering = ["module", "sort_order", "label"]

    def __str__(self) -> str:
        return self.label


class StaffRoleCapability(models.Model):
    """Role->capability mapping."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(StaffRole, on_delete=models.CASCADE, related_name="capability_links")
    capability = models.ForeignKey(StaffCapability, on_delete=models.CASCADE, related_name="role_links")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "staff_role_capabilities"
        constraints = [
            models.UniqueConstraint(fields=["role", "capability"], name="uniq_staff_role_capability"),
        ]


class StaffCapabilityOverride(models.Model):
    """Optional per-staff override: grant or revoke."""

    MODE_GRANT = "grant"
    MODE_REVOKE = "revoke"
    MODES = ((MODE_GRANT, "Grant"), (MODE_REVOKE, "Revoke"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey("HospitalStaff", on_delete=models.CASCADE, related_name="capability_overrides")
    capability = models.ForeignKey(StaffCapability, on_delete=models.CASCADE, related_name="staff_overrides")
    mode = models.CharField(max_length=10, choices=MODES, default=MODE_GRANT)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "staff_capability_overrides"
        constraints = [
            models.UniqueConstraint(
                fields=["staff", "capability", "mode"], name="uniq_staff_capability_override"
            ),
        ]


class HospitalStaff(models.Model):
    """Roster row for hospital employees (further-studies applicants, HODs, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hospital_staff_profile",
    )
    staff_number = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                r"^((MMH-\d{4}-\d{4})|(H\d{3}))$",
                "Must match MMH-YYYY-XXXX or practice staff id H### (e.g. H001).",
            ),
        ],
    )
    full_name = models.CharField(max_length=100)
    department = models.ForeignKey(
        "hospital_directory.Department",
        on_delete=models.PROTECT,
        related_name="hospital_staff_members",
        null=True,
        blank=True,
    )
    designation = models.ForeignKey(
        "hospital_directory.Designation",
        on_delete=models.PROTECT,
        related_name="hospital_staff_members",
        null=True,
        blank=True,
    )
    working_site = models.ForeignKey(
        "hospital_directory.WorkingSite",
        on_delete=models.PROTECT,
        related_name="hospital_staff_members",
        null=True,
        blank=True,
    )
    phone = models.CharField(max_length=20)
    national_id = models.CharField(max_length=50)
    date_employed = models.DateField()
    staff_role = models.ForeignKey(
        StaffRole,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="staff_members",
    )
    hod = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hod_subordinates",
    )
    # Legacy direct capabilities storage; superseded by role_capabilities + overrides.
    capabilities = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "hospital_staff"
        ordering = ["staff_number"]

    def __str__(self) -> str:
        return f"{self.staff_number} — {self.full_name}"


class DepartmentHodAssignment(models.Model):
    """Department -> HOD mapping for review routing."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(
        "hospital_directory.Department",
        on_delete=models.CASCADE,
        related_name="hod_assignments",
    )
    hod_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="department_hod_assignments",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "department_hod_assignments"
        ordering = ["department__name"]
        constraints = [
            models.UniqueConstraint(fields=["department"], name="uniq_department_hod_assignment"),
        ]

    def __str__(self) -> str:
        return f"{self.department_id} -> {self.hod_user_id}"

