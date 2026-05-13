from django.contrib import admin

from .models import ImportBatch


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = (
        "file_name",
        "batch_type",
        "status",
        "total_rows",
        "success_rows",
        "failed_rows",
        "imported_by",
        "created_at",
    )
    list_filter = ("batch_type", "status")
