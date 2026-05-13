from django.db import models


class UserRole(models.TextChoices):
    HOSPITAL_STAFF = "hospital_staff", "Hospital staff"
    STUDENT = "student", "Student"
    HOD = "hod", "Head of Department"
    ASST_DIRECTOR = "asst_director", "Assistant Director"
    MANAGEMENT = "management", "Management"
    HOSPITAL_ADMIN = "hospital_admin", "Hospital Admin"
    UNIV_ADMIN = "univ_admin", "University Admin"
    SYSADMIN = "sysadmin", "System Admin"


# All roles that can hold a HospitalStaff profile and have capabilities assigned.
HOSPITAL_WORKER_ROLES = frozenset({
    UserRole.HOSPITAL_STAFF,
    UserRole.HOD,
    UserRole.ASST_DIRECTOR,
    UserRole.MANAGEMENT,
})

# Roles allowed to create, view, edit, and delete student records.
STUDENT_MANAGER_ROLES = frozenset({
    UserRole.UNIV_ADMIN,
    UserRole.HOSPITAL_ADMIN,
    UserRole.SYSADMIN,
})


class UserModule(models.TextChoices):
    FURTHER_STUDIES = "further_studies", "Further Studies"
    ATTACHMENT = "attachment", "Attachment"
    ADMIN = "admin", "Admin"


class ApplicationType(models.TextChoices):
    FURTHER_STUDIES = "further_studies", "Further Studies"
    ATTACHMENT = "attachment", "Field Attachment"


class ApplicationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    RETURNED = "returned", "Returned"


class ReviewStage(models.TextChoices):
    HOD = "hod", "HOD"
    ASST_DIRECTOR = "asst_director", "Assistant Director"
    MANAGEMENT = "management", "Management"
    HR = "hr", "HR (field attachment)"


class StaffCapability(models.TextChoices):
    """Granted by hospital admin on `HospitalStaff`; role stays `hospital_staff`."""

    HR_FIELD_REQUESTS = "hr_field_requests", "HR — student field / attachment requests"
    HOD_VIEW_DEPARTMENT_STAFF = "hod_view_department_staff", "HOD — view department staff roster"


class ReviewDecision(models.TextChoices):
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    RETURNED = "returned", "Returned"


class NotificationType(models.TextChoices):
    SUBMISSION = "submission", "Submission"
    APPROVAL = "approval", "Approval"
    REJECTION = "rejection", "Rejection"
    REVISION = "revision", "Revision"
    FIELD_PLACEMENT_PUBLISHED = "field_placement_published", "Field placement published"


class ImportBatchType(models.TextChoices):
    HOSPITAL_STAFF = "hospital_staff", "Hospital staff"
    STUDENT = "student", "Student"


class ImportBatchStatus(models.TextChoices):
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
    UNSPECIFIED = "unspecified", "Prefer not to say"


class PlacementScope(models.TextChoices):
    """Attachment / placement request: cohort vs single student."""
    INDIVIDUAL = "individual", "Individual"
    GROUP = "group", "Group"
