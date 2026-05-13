import strawberry_django

from apps.imports.models import ImportBatch
from apps.users.graphql.types import UserType


@strawberry_django.type(
    ImportBatch,
    fields=[
        "id",
        "batch_type",
        "file_name",
        "total_rows",
        "success_rows",
        "failed_rows",
        "status",
        "created_at",
    ],
)
class ImportBatchType:
    @strawberry_django.field()
    def imported_by(self, root: ImportBatch) -> UserType:
        from apps.users.models import User

        return User.objects.get(pk=root.imported_by_id)
