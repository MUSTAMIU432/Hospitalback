from django.contrib import admin

from .models import Application, ApplicationDocument, ReviewTrail


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "app_ref",
        "applicant",
        "app_type",
        "status",
        "current_stage",
        "updated_at",
    )
    list_filter = ("app_type", "status", "current_stage")
    search_fields = ("app_ref",)


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "doc_type", "uploaded_at")


@admin.register(ReviewTrail)
class ReviewTrailAdmin(admin.ModelAdmin):
    list_display = ("application", "reviewer", "stage", "decision", "reviewed_at")
