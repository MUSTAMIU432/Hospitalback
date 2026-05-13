from django.contrib import admin

from .models import DepartmentHodAssignment, HospitalStaff


@admin.register(HospitalStaff)
class HospitalStaffAdmin(admin.ModelAdmin):
    list_display = (
        "staff_number",
        "full_name",
        "department",
        "designation",
        "working_site",
        "hod",
        "capabilities",
    )
    search_fields = ("staff_number", "full_name", "national_id")


@admin.register(DepartmentHodAssignment)
class DepartmentHodAssignmentAdmin(admin.ModelAdmin):
    list_display = ("department", "hod_user", "is_active", "updated_at")
    list_filter = ("is_active", "department")
    search_fields = ("department__name", "hod_user__username", "hod_user__first_name", "hod_user__last_name")
