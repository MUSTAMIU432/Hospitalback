import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants import UserModule, UserRole


class User(AbstractUser):
    """Central authentication record (STUD spec)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        _("username"),
        max_length=50,
        unique=True,
        help_text=_("Employee number or student registration number."),
    )
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.HOSPITAL_STAFF,
    )
    module = models.CharField(
        max_length=30,
        choices=UserModule.choices,
        default=UserModule.FURTHER_STUDIES,
    )
    is_first_login = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["username"]

    def save(self, *args, **kwargs):
        # Django superusers (createsuperuser / is_superuser) map to STUD platform admin.
        if self.is_superuser:
            self.role = UserRole.SYSADMIN
            self.module = UserModule.ADMIN
            self.is_staff = True
            self.is_first_login = False
        elif self.role in (
            UserRole.SYSADMIN,
            UserRole.HOSPITAL_ADMIN,
        ):
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username
