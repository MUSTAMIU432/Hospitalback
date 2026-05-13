import strawberry
from django.core.exceptions import PermissionDenied
from strawberry.types import Info

from apps.imports.graphql.types import ImportBatchType
from apps.imports.models import ImportBatch
from apps.users.graphql.auth import require_auth
from core.constants import ImportBatchType as BatchTypeEnum
from core.constants import UserRole


@strawberry.type
class ImportsQuery:
    @strawberry.field
    def import_batches(self, info: Info) -> list[ImportBatchType]:
        user = require_auth(info)
        role = getattr(user, "role", None)
        if role == UserRole.HOSPITAL_ADMIN:
            return list(
                ImportBatch.objects.filter(batch_type=BatchTypeEnum.HOSPITAL_STAFF)[:100]
            )
        if role == UserRole.UNIV_ADMIN:
            return list(ImportBatch.objects.filter(batch_type=BatchTypeEnum.STUDENT)[:100])
        raise PermissionDenied("Not allowed.")
