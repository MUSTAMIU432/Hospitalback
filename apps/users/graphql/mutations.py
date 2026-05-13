import strawberry
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied, ValidationError
from strawberry.types import Info

from apps.employees.models import HospitalStaff
from apps.students.models import StudentProfile
from apps.users.graphql.auth import require_auth
from apps.users.services.staff_credentials import hospital_staff_login_password_ok
from apps.users.services.student_credentials import student_login_password_ok
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
