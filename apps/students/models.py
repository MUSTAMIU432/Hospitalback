import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from core.constants import Gender
from core.validators import validate_dob_ddmmyyyy


class UniversityFaculty(models.Model):
    """University faculty (univ admin). Departments hang under a faculty."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "university_faculties"
        ordering = ["sort_order", "name"]
        verbose_name_plural = "University faculties"

    def __str__(self) -> str:
        return self.name


class UniversityDepartment(models.Model):
    """Academic department under a faculty."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty = models.ForeignKey(
        UniversityFaculty,
        on_delete=models.CASCADE,
        related_name="departments",
    )
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "university_departments"
        ordering = ["faculty", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["faculty", "name"],
                name="uniq_university_department_per_faculty",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.faculty.name} / {self.name}"


class StudentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    registration_no = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                r"^((ZU/[A-Z]{2,6}/\d{4}/\d{4})|(S\d{3}))$",
                "Must match ZU/PROG/YYYY/XXXX or practice student id S### (e.g. S001).",
            ),
        ],
    )
    full_name = models.CharField(max_length=100)
    programme = models.CharField(max_length=100, help_text="Course / programme of study.")
    faculty = models.CharField(max_length=100)
    faculty_entity = models.ForeignKey(
        UniversityFaculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profiles",
    )
    department_entity = models.ForeignKey(
        UniversityDepartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profiles",
    )
    level_of_study = models.CharField(
        max_length=30,
        blank=True,
        default="",
        help_text="e.g. degree, diploma, masters",
    )
    year_of_study = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
    )
    phone = models.CharField(max_length=20)
    contact_email = models.EmailField(blank=True, default="")
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.UNSPECIFIED,
    )
    dob = models.CharField(
        max_length=20,
        help_text="DDMMYYYY as stored for default password workflow.",
        validators=[validate_dob_ddmmyyyy],
    )
    university = models.CharField(max_length=100, default="Zanzibar University")
    hospital_department = models.ForeignKey(
        "hospital_directory.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profiles",
        help_text="Hospital department corresponding to placement / attachment.",
    )
    dashboard_notes = models.TextField(
        blank=True,
        default="",
        help_text="Extra dashboard / admin-visible notes for this student.",
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervised_students",
    )

    class Meta:
        db_table = "student_profiles"
        ordering = ["registration_no"]

    def __str__(self) -> str:
        return f"{self.registration_no} — {self.full_name}"
