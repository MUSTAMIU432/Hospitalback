from django.contrib import admin

from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("registration_no", "full_name", "programme", "user", "supervisor")
    search_fields = ("registration_no", "full_name")
