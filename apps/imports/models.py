import uuid

from django.conf import settings
from django.db import models

from core.constants import ImportBatchStatus, ImportBatchType


class ImportBatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="import_batches",
    )
    batch_type = models.CharField(max_length=20, choices=ImportBatchType.choices)
    file_name = models.CharField(max_length=255)
    total_rows = models.PositiveIntegerField(default=0)
    success_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=30,
        choices=ImportBatchStatus.choices,
        default=ImportBatchStatus.PROCESSING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "import_batches"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.batch_type} {self.file_name} ({self.status})"
