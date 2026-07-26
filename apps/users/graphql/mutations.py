import logging
import uuid

import strawberry
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied, ValidationError
from strawberry.types import Info

from apps.employees.models import HospitalStaff
from apps.students.models import StudentProfile
from apps.users.graphql.auth import require_auth
from apps.users.services.google_auth import GoogleAuthError, login_with_google as google_login
from apps.users.services.password_reset import (
    PasswordResetError,
    request_password_reset as request_password_reset_service,
    reset_password as reset_password_service,
)
from apps.users.services.staff_credentials import hospital_staff_login_password_ok
from apps.users.services.student_credentials import (
    student_default_password_from_full_name,
    student_login_password_ok,
)
from apps.users.graphql.types import AuthPayload, OperationResult, UserType
from apps.users.jwt_utils import (
    get_user_from_refresh_token,
    issue_access_token,
    issue_refresh_token,
)
from apps.users.models import User
from apps.users.services import provisioning
from core.constants import UserRole
from strawberry_django.utils.requests import get_request

logger = logging.getLogger(__name__)

_TENANT_ADMIN_ROLES = {UserRole.HOSPITAL_ADMIN, UserRole.UNIV_ADMIN}


def _require_sysadmin_and_get_admin(info: Info, user_id: uuid.UUID) -> User:
    """Authorise the sysadmin caller and return the target tenant-admin user."""
    acting = require_auth(info)
    if getattr(acting, "role", None) != UserRole.SYSADMIN:
        raise PermissionDenied("Only system administrators may manage tenant administrators.")
    try:
        target = User.objects.get(pk=user_id)
    except User.DoesNotExist as exc:
        raise ValidationError("Administrator not found.") from exc
    if target.role not in _TENANT_ADMIN_ROLES:
        raise ValidationError("This user is not a hospital or university administrator.")
    return target


@strawberry.type
class UsersMutation:
    @strawberry.mutation
    def login(self, info: Info, username: str, password: str) -> AuthPayload:
        username = username.strip()
        request = get_request(info)
        user = authenticate(request, username=username, password=password)
        # Students may sign in with registration number while User.username is studprac_* (practice seed).
        if user is None:
            try:
                profile = StudentProfile.objects.select_related("user").get(registration_no=username)
                cand = profile.user
                if student_login_password_ok(user=cand, profile=profile, password=password):
                    user = cand
            except StudentProfile.DoesNotExist:
                pass
            # Username may still equal User.username if profile.registration_no differs (legacy rows).
            if user is None:
                try:
                    cand = User.objects.get(username=username, role=UserRole.STUDENT)
                    profile = StudentProfile.objects.get(user=cand)
                    if student_login_password_ok(user=cand, profile=profile, password=password):
                        user = cand
                except (User.DoesNotExist, StudentProfile.DoesNotExist):
                    pass
            if user is None:
                try:
                    cand = User.objects.get(username=username, role=UserRole.HOSPITAL_STAFF)
                    profile = HospitalStaff.objects.get(user=cand)
                    if hospital_staff_login_password_ok(user=cand, profile=profile, password=password):
                        user = cand
                except (User.DoesNotExist, HospitalStaff.DoesNotExist):
                    pass
        if user is None or not user.is_active:
            raise PermissionDenied("Invalid credentials.")
        access = issue_access_token(user.pk)
        refresh = issue_refresh_token(user.pk)
        user_orm = User.objects.get(pk=user.pk)
        return AuthPayload(
            access_token=access,
            refresh_token=refresh,
            token_type="Bearer",
            user=user_orm,
        )

    @strawberry.mutation
    def login_with_google(self, info: Info, credential: str) -> AuthPayload:
        """Exchange a Google ID token for STUD access/refresh tokens.

        `credential` is the JWT that Google Identity Services hands the browser.
        It is verified server-side (signature, audience, issuer, expiry) before
        any user is resolved — see services.google_auth.
        """
        try:
            user = google_login(credential)
        except GoogleAuthError as exc:
            raise PermissionDenied(str(exc)) from exc

        return AuthPayload(
            access_token=issue_access_token(user.pk),
            refresh_token=issue_refresh_token(user.pk),
            token_type="Bearer",
            user=User.objects.get(pk=user.pk),
        )

    @strawberry.mutation
    def request_password_reset(self, info: Info, email: str) -> OperationResult:
        """Email a reset link. Always reports success.

        The response is intentionally identical whether or not the address is
        registered — a differing reply would turn this into an account-existence
        oracle for anyone able to guess addresses.
        """
        request = get_request(info)
        ip = None
        if request is not None:
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
            ip = forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR")

        try:
            request_password_reset_service(email=email, ip=ip)
        except Exception:  # noqa: BLE001
            # SMTP failures must not reveal that the address matched an account.
            logger.exception("Password reset email failed for %r", email)

        return OperationResult(
            ok=True,
            message="If an account exists for that address, a reset link is on its way.",
        )

    @strawberry.mutation
    def reset_password(self, info: Info, token: str, new_password: str) -> OperationResult:
        try:
            reset_password_service(raw_token=token, new_password=new_password)
        except PasswordResetError as exc:
            raise ValidationError(str(exc)) from exc
        return OperationResult(
            ok=True,
            message="Password updated. You can now sign in with your new password.",
        )

    @strawberry.mutation
    def change_password(
        self,
        info: Info,
        old_password: str | None = None,
        new_password: str = "",
    ) -> OperationResult:
        user = require_auth(info)
        if not new_password or len(new_password) < 8:
            raise ValidationError("New password must be at least 8 characters.")
        if user.is_first_login:
            user.set_password(new_password)
            user.is_first_login = False
            user.save(update_fields=["password", "is_first_login"])
            return OperationResult(ok=True, message="Password updated.")
        if not old_password or not user.check_password(old_password):
            raise PermissionDenied("Current password is incorrect.")
        user.set_password(new_password)
        user.is_first_login = False
        user.save(update_fields=["password", "is_first_login"])
        return OperationResult(ok=True, message="Password updated.")

    @strawberry.mutation
    def create_tenant_admin(
        self,
        info: Info,
        username: str,
        role: str,
        password: str | None = None,
        email: str = "",
        first_name: str = "",
    ) -> UserType:
        acting = require_auth(info)
        user = provisioning.create_tenant_admin_user(
            acting_user=acting,
            username=username,
            password=password,
            role=role.strip(),
            email=email,
            first_name=first_name,
        )
        return User.objects.get(pk=user.pk)

    @strawberry.mutation
    def update_tenant_admin(
        self,
        info: Info,
        user_id: uuid.UUID,
        first_name: str | None = None,
        email: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
    ) -> UserType:
        """Sysadmin: edit a tenant administrator's display name, email, role, or active state."""
        target = _require_sysadmin_and_get_admin(info, user_id)
        fields: list[str] = []
        if first_name is not None:
            target.first_name = first_name.strip()[:150]
            fields.append("first_name")
        if email is not None:
            target.email = email.strip()
            fields.append("email")
        if role is not None:
            r = role.strip()
            if r not in {UserRole.HOSPITAL_ADMIN, UserRole.UNIV_ADMIN}:
                raise ValidationError("Role must be hospital admin or university admin.")
            target.role = r
            fields.append("role")
        if is_active is not None:
            target.is_active = bool(is_active)
            fields.append("is_active")
        if fields:
            target.save(update_fields=fields)
        return User.objects.get(pk=target.pk)

    @strawberry.mutation
    def reset_tenant_admin_password(self, info: Info, user_id: uuid.UUID) -> OperationResult:
        """Sysadmin: reset an admin to the default temp password (first word of display
        name) and force a password change on next login. Returns the temp password."""
        target = _require_sysadmin_and_get_admin(info, user_id)
        temp = student_default_password_from_full_name(target.first_name or target.username)
        if not temp:
            raise ValidationError(
                "Cannot derive a temp password — set a display name with at least one word first."
            )
        target.set_password(temp)
        target.is_first_login = True
        target.save(update_fields=["password", "is_first_login"])
        return OperationResult(ok=True, message=temp)

    @strawberry.mutation
    def delete_tenant_admin(self, info: Info, user_id: uuid.UUID) -> OperationResult:
        """Sysadmin: permanently delete a tenant administrator account."""
        target = _require_sysadmin_and_get_admin(info, user_id)
        uname = target.username
        target.delete()
        return OperationResult(ok=True, message=f"Administrator {uname} deleted.")

    @strawberry.mutation
    def refresh_token(self, info: Info, token: str) -> AuthPayload:
        """Issue a new access (and refresh) token pair; does not require Authorization header."""
        rt = token.strip()
        user = get_user_from_refresh_token(rt)
        if user is None:
            raise PermissionDenied("Invalid or expired refresh token.")
        user_orm = User.objects.get(pk=user.pk)
        return AuthPayload(
            access_token=issue_access_token(user.pk),
            refresh_token=issue_refresh_token(user.pk),
            token_type="Bearer",
            user=user_orm,
        )
