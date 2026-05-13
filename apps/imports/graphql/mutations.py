import base64

import strawberry
from django.core.exceptions import PermissionDenied, ValidationError
from strawberry.types import Info

from apps.imports.graphql.types import ImportBatchType
from apps.imports.models import ImportBatch
from apps.imports.services import excel_import
from apps.users.graphql.auth import require_auth
from apps.users.graphql.types import OperationResult
from core.constants import ImportBatchType as BatchTypeEnum
from core.constants import UserRole


@strawberry.type
class ImportsMutation:
    def _assert_batch_access(self, acting, batch: ImportBatch) -> None:
        role = getattr(acting, "role", None)
        if role == UserRole.HOSPITAL_ADMIN and batch.batch_type == BatchTypeEnum.HOSPITAL_STAFF:
            return
        if role == UserRole.UNIV_ADMIN and batch.batch_type == BatchTypeEnum.STUDENT:
            return
        raise PermissionDenied("Not allowed.")

    @strawberry.mutation
    def import_hospital_staff_excel_base64(
        self,
        info: Info,
        file_name: str,
        file_base64: str,
    ) -> ImportBatchType:
        acting = require_auth(info)
        role = getattr(acting, "role", None)
        if role != UserRole.HOSPITAL_ADMIN:
            raise PermissionDenied("Not allowed.")
        data = base64.b64decode(file_base64)
        return excel_import.import_hospital_staff_from_xlsx(
            file_bytes=data,
            file_name=file_name,
            acting_user=acting,
        )

    @strawberry.mutation
    def import_students_excel_base64(
        self,
        info: Info,
        file_name: str,
        file_base64: str,
    ) -> ImportBatchType:
        acting = require_auth(info)
        role = getattr(acting, "role", None)
        if role != UserRole.UNIV_ADMIN:
            raise PermissionDenied("Not allowed.")
        data = base64.b64decode(file_base64)
        return excel_import.import_students_from_xlsx(
            file_bytes=data,
            file_name=file_name,
            acting_user=acting,
        )

    @strawberry.mutation
    def update_import_batch_file_name(
        self,
        info: Info,
        batch_id: strawberry.ID,
        file_name: str,
    ) -> ImportBatchType:
        acting = require_auth(info)
        try:
            batch = ImportBatch.objects.get(pk=batch_id)
        except ImportBatch.DoesNotExist as exc:
            raise ValidationError("Import batch not found.") from exc
        self._assert_batch_access(acting, batch)
        next_name = file_name.strip()
        if not next_name:
            raise ValidationError("File name is required.")
        batch.file_name = next_name
        batch.save(update_fields=["file_name"])
        return batch

    @strawberry.mutation
    def delete_import_batch(self, info: Info, batch_id: strawberry.ID) -> OperationResult:
        acting = require_auth(info)
        try:
            batch = ImportBatch.objects.get(pk=batch_id)
        except ImportBatch.DoesNotExist as exc:
            raise ValidationError("Import batch not found.") from exc
        self._assert_batch_access(acting, batch)
        batch.delete()
        return OperationResult(ok=True, message="Import batch deleted.")
