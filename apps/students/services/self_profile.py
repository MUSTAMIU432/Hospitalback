"""Student-completed profile: the self-service half of admin registration.

A student who signed up themselves (form or Google) has a `User` but no
`StudentProfile`. This module lets them fill in exactly the fields an
administrator would have filled in via `provisioning.create_student_user`, with
the same validation, and nothing more:

  * no `supervisor` — that is an assignment, not a self-declaration
  * no `hospital_department` — that is a placement decision
  * no `dashboard_notes` — staff-authored

Those stay empty until someone with the authority to set them does.
"""

from __future__ import annotations

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from django.db import transaction

from apps.students.models import StudentProfile, UniversityDepartment, UniversityFaculty
from core.constants import Gender, UserRole
from core.validators import validate_dob_ddmmyyyy, validate_registration_no

_LEVELS = {"degree", "diploma", "masters", "phd"}


def profile_is_complete(user) -> bool:
    """True when *user* needs no profile-completion step.

    Only students are ever gated — every other role's profile is created by an
    administrator as part of provisioning, so the question does not arise.
    """
    if getattr(user, "role", None) != UserRole.STUDENT:
        return True
    return StudentProfile.objects.filter(user=user).exists()


@transaction.atomic
def complete_student_profile(
    *,
    user,
    registration_no: str,
    full_name: str,
    programme: str,
    faculty: str,
    year_of_study: int,
    phone: str,
    dob: str,
    university: str,
    gender: str = Gender.UNSPECIFIED,
    level_of_study: str = "",
    middle_name: str = "",
    contact_email: str = "",
    faculty_entity_id=None,
    department_entity_id=None,
) -> StudentProfile:
    if getattr(user, "role", None) != UserRole.STUDENT:
        raise PermissionDenied("Only student accounts have a student profile.")
    if StudentProfile.objects.filter(user=user).exists():
        raise ValidationError(
            "Your profile is already set up. Ask an administrator to change these details."
        )

    registration_no = (registration_no or "").strip().upper()
    # Raises with the canonical message, so the SPA can show the required format
    # verbatim rather than paraphrasing it.
    validate_registration_no(registration_no)
    if StudentProfile.objects.filter(registration_no__iexact=registration_no).exists():
        raise ValidationError(
            "That registration number is already registered. "
            "If it is yours, contact your administrator — you may already have an account."
        )

    full_name = (full_name or "").strip()
    if not full_name:
        raise ValidationError("Full name is required.")

    programme = (programme or "").strip()
    if not programme:
        raise ValidationError("Programme is required.")

    phone = (phone or "").strip()
    if not phone:
        raise ValidationError("Phone number is required.")

    dob = (dob or "").strip()
    validate_dob_ddmmyyyy(dob)

    if year_of_study is None or not 1 <= int(year_of_study) <= 6:
        raise ValidationError("Year of study must be between 1 and 6.")

    if gender not in {c.value for c in Gender}:
        raise ValidationError("Invalid gender value.")

    # Falls back to the address they registered with. Validated even though it
    # came from us originally, because the form lets them override it — and an
    # unreachable contact address means a lost placement notification.
    contact_email = (contact_email or "").strip().lower() or (user.email or "").strip().lower()
    if contact_email:
        try:
            validate_email(contact_email)
        except ValidationError as exc:
            # Replaces Django's terse "Enter a valid email address." with the
            # same text but raised from our own path, so the SPA's error
            # surfacing stays uniform across every field on this form.
            raise ValidationError("Enter a valid email address.") from exc

    level_of_study = (level_of_study or "").strip().lower()
    if level_of_study and level_of_study not in _LEVELS:
        raise ValidationError("Invalid level of study.")

    # Resolve the registry FKs and let them win over the free-text faculty name,
    # mirroring create_student_user so both paths store the same canonical value.
    fac_obj: UniversityFaculty | None = None
    dep_obj: UniversityDepartment | None = None
    faculty_display = (faculty or "").strip()

    if faculty_entity_id:
        fac_obj = UniversityFaculty.objects.filter(pk=faculty_entity_id).first()
        if fac_obj is None:
            raise ValidationError("Selected faculty no longer exists.")
        faculty_display = fac_obj.name
    if department_entity_id:
        dep_obj = (
            UniversityDepartment.objects.select_related("faculty")
            .filter(pk=department_entity_id)
            .first()
        )
        if dep_obj is None:
            raise ValidationError("Selected department no longer exists.")
        if fac_obj is not None and dep_obj.faculty_id != fac_obj.id:
            raise ValidationError("That department does not belong to the selected faculty.")
        fac_obj = fac_obj or dep_obj.faculty
        faculty_display = dep_obj.faculty.name

    if not faculty_display:
        raise ValidationError("Faculty is required.")

    profile = StudentProfile.objects.create(
        user=user,
        registration_no=registration_no,
        full_name=full_name,
        middle_name=(middle_name or "").strip()[:60],
        programme=programme,
        faculty=faculty_display,
        faculty_entity=fac_obj,
        department_entity=dep_obj,
        level_of_study=level_of_study[:30],
        year_of_study=int(year_of_study),
        phone=phone,
        contact_email=contact_email,
        gender=gender,
        dob=dob,
        university=(university or "").strip() or "Zanzibar University",
    )

    # Keep the User row consistent with what admin-created students look like:
    # first/last name derived from the declared full name, so staff-facing lists
    # that read User.first_name show the same person as the profile does.
    parts = full_name.split()
    if parts:
        user.first_name = parts[0][:150]
        if len(parts) > 1:
            user.last_name = parts[-1][:150]
        user.save(update_fields=["first_name", "last_name"])

    return profile
