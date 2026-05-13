import re

from django.core.exceptions import ValidationError


def validate_staff_number(value: str) -> None:
    if not re.fullmatch(r"^((MMH-\d{4}-\d{4})|(H\d{3}))$", value or ""):
        raise ValidationError(
            "Staff number must match MMH-YYYY-XXXX or practice format H### (e.g. H001)."
        )


def validate_registration_no(value: str) -> None:
    if not re.fullmatch(r"^((ZU/[A-Z]{2,6}/\d{4}/\d{4})|(S\d{3}))$", value or ""):
        raise ValidationError(
            "Registration number must match ZU/PROG/YYYY/XXXX or practice format S### (e.g. S001)."
        )


def validate_dob_ddmmyyyy(value: str) -> None:
    if not re.fullmatch(r"^\d{8}$", value or ""):
        raise ValidationError("Date of birth must be DDMMYYYY (8 digits).")
