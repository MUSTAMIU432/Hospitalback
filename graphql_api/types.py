"""
Re-exports of app-level GraphQL types (single import path for tooling / clients).
Prefer importing from ``apps.<app>.graphql.types`` in new code.
"""

from apps.applications.graphql.types import (  # noqa: F401
    ApplicantStudentProfileType,
    ApplicationDocumentType,
    ApplicationType,
    PdfPayload,
    ReviewTrailType,
)
from apps.employees.graphql.types import HospitalStaffType  # noqa: F401
from apps.imports.graphql.types import ImportBatchType  # noqa: F401
from apps.notifications.graphql.types import NotificationType  # noqa: F401
from apps.reports.graphql.types import DashboardDigest, StatusCount  # noqa: F401
from apps.students.graphql.types import StudentProfileType  # noqa: F401
from apps.users.graphql.types import AuthPayload, OperationResult, UserType  # noqa: F401
