import base64
import mimetypes
import uuid

import strawberry
from django.core.exceptions import PermissionDenied
from strawberry.types import Info

from apps.applications.graphql.types import ApplicationType, EncodedFilePayload
from apps.applications.models import Application, ApplicationDocument
from apps.applications.services import access as access_svc
from apps.applications.services import workflow
from apps.users.graphql.auth import require_auth
from core.constants import UserRole


@strawberry.type
class StudyRequestsQuery:
    @strawberry.field
    def my_applications(self, info: Info) -> list[ApplicationType]:
        user = require_auth(info)
        return list(access_svc.applications_for_applicant(user))

    @strawberry.field
    def review_queue(self, info: Info) -> list[ApplicationType]:
        user = require_auth(info)
        return list(access_svc.applications_in_review_queues(user))

    @strawberry.field
    def applications_with_management_final_letters(self, info: Info) -> list[ApplicationType]:
        """
        Applications that have a stored Top Management formal letter (review trail).
        Persists after final approval — used by /reviewer/final-letter for HOD, ADR, and Management.
        """
        user = require_auth(info)
        if not access_svc.can_query_management_final_letters(user):
            raise PermissionDenied("You cannot access Top Management final letters.")
        return access_svc.applications_with_management_final_letters(user)

    @strawberry.field
    def application(self, info: Info, id: strawberry.ID) -> ApplicationType | None:
        user = require_auth(info)
        try:
            app = Application.objects.get(pk=id)
        except Application.DoesNotExist:
            return None
        workflow.assert_can_view(user, app)
        return app

    @strawberry.field
    def field_placements_for_university(self, info: Info) -> list[ApplicationType]:
        user = require_auth(info)
        if getattr(user, "role", None) != UserRole.UNIV_ADMIN:
            raise PermissionDenied("Only university administrators may list published field placements.")
        return list(access_svc.field_placements_visible_to_university())

    @strawberry.field
    def review_feedback_letter_template(
        self,
        info: Info,
        application_id: uuid.UUID,
        signer_placeholder: str = "",
    ) -> EncodedFilePayload:
        """Server-rendered HTML template for the formal review feedback letter (download or import)."""
        user = require_auth(info)
        app = Application.objects.select_related("applicant").get(pk=application_id)
        workflow.assert_can_view(user, app)
        html = workflow.render_review_feedback_letter_template_html(
            app, signer_placeholder=signer_placeholder
        )
        ref = (app.app_ref or str(app.id)).replace("/", "-")
        return EncodedFilePayload(
            filename=f"review-feedback-template-{ref}.html",
            content_base64=base64.b64encode(html.encode("utf-8")).decode("ascii"),
            mime_type="text/html; charset=utf-8",
        )

    @strawberry.field
    def review_feedback_uploaded_letter(
        self,
        info: Info,
        document_id: uuid.UUID,
    ) -> EncodedFilePayload:
        """Download an uploaded review feedback letter (`review_feedback_letter`) as base64."""
        user = require_auth(info)
        doc = ApplicationDocument.objects.select_related("application").get(pk=document_id)
        workflow.assert_can_download_review_feedback_document(user, doc)
        name = (doc.file.name or "letter").rsplit("/", maxsplit=1)[-1]
        with doc.file.open("rb") as f:
            raw = f.read()
        mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
        return EncodedFilePayload(
            filename=name or "review-feedback-letter.bin",
            content_base64=base64.b64encode(raw).decode("ascii"),
            mime_type=mime,
        )


ApplicationsQuery = StudyRequestsQuery
