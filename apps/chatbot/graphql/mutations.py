import uuid
from typing import Optional

import strawberry
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from strawberry.types import Info

from apps.chatbot.graphql.types import (
    ChatHistoryInput,
    ChatOperationResult,
    ComposeContextInput,
    GeneratedTextType,
    WorkflowChatReply,
)
from apps.chatbot.models import ChatInteraction, KnowledgeEntry, KnowledgeSource
from apps.chatbot.services import compose
from apps.chatbot.services import knowledge as kb
from apps.chatbot.services import provider
from apps.chatbot.services.roles import chat_role_for
from apps.users.graphql.auth import require_auth

MAX_MESSAGE_CHARS = 2000


@strawberry.type
class ChatbotMutation:
    @strawberry.mutation
    def workflow_chat(
        self,
        info: Info,
        message: str,
        history: Optional[list[ChatHistoryInput]] = None,
        contribute: bool = False,
    ) -> WorkflowChatReply:
        """Answer a question from the knowledge base, phrased by the provider.

        ``contribute`` is the user's opt-in from chat settings: only then is the
        exchange stored, and only stored exchanges can be rated and promoted.
        """
        user = require_auth(info)
        body = (message or "").strip()
        if not body:
            raise ValidationError("Message is required.")
        if len(body) > MAX_MESSAGE_CHARS:
            raise ValidationError(f"Message is too long (limit {MAX_MESSAGE_CHARS} characters).")

        role = chat_role_for(user)
        entries = kb.search(body, role, limit=4)
        reply = provider.ask(
            question=body,
            role=role,
            history=[{"role": h.role, "text": h.text} for h in (history or [])],
            entries=entries,
        )

        interaction_id = None
        if contribute:
            interaction = ChatInteraction.objects.create(
                user=user,
                role=role,
                question=body,
                answer=reply.answer,
                provider=reply.provider,
                model=reply.model,
                used_fallback=reply.used_fallback,
                matched_keys=",".join(e.key for e in entries),
            )
            interaction_id = str(interaction.id)

        return WorkflowChatReply(
            ok=True,
            answer=reply.answer,
            provider=reply.provider,
            model=reply.model,
            used_fallback=reply.used_fallback,
            interaction_id=interaction_id,
            sources=[e.title for e in entries],
            suggestions=kb.suggestions_for(role),
        )

    @strawberry.mutation
    def rate_chat_answer(self, info: Info, interaction_id: uuid.UUID, helpful: bool) -> ChatOperationResult:
        """Thumbs up/down. A thumbs-up parks the exchange as a draft knowledge
        entry for an admin to review — it is never served until approved."""
        user = require_auth(info)
        interaction = ChatInteraction.objects.filter(pk=interaction_id, user=user).first()
        if interaction is None:
            raise ValidationError("Conversation entry not found.")

        interaction.helpful = helpful
        if helpful and interaction.promoted_entry_id is None and not interaction.used_fallback:
            base = slugify(interaction.question)[:90] or "learned"
            key = f"learned-{base}"
            suffix = 1
            while KnowledgeEntry.objects.filter(key=key).exists():
                suffix += 1
                key = f"learned-{base}-{suffix}"[:120]
            entry = KnowledgeEntry.objects.create(
                key=key,
                title=interaction.question[:200],
                body=interaction.answer,
                roles=interaction.role,
                tags=",".join(kb.keywords(interaction.question)[:12]),
                source=KnowledgeSource.LEARNED,
                is_active=False,  # awaits admin approval
            )
            interaction.promoted_entry = entry
        interaction.save(update_fields=["helpful", "promoted_entry"])
        return ChatOperationResult(
            ok=True,
            message="Thanks — noted." if helpful else "Thanks, we'll use that to improve answers.",
        )

    @strawberry.mutation
    def clear_chat_contributions(self, info: Info) -> ChatOperationResult:
        """Delete everything this user contributed. Draft entries learned from
        those exchanges go too; approved ones stay, as they are now shared."""
        user = require_auth(info)
        interactions = ChatInteraction.objects.filter(user=user)
        KnowledgeEntry.objects.filter(
            learned_from__user=user,
            source=KnowledgeSource.LEARNED,
            is_active=False,
        ).delete()
        count = interactions.count()
        interactions.delete()
        return ChatOperationResult(ok=True, message=f"Removed {count} stored conversation(s).", count=count)

    @strawberry.mutation
    def generate_field_text(
        self,
        info: Info,
        field: str,
        context: Optional[list[ComposeContextInput]] = None,
        instruction: str = "",
        existing: str = "",
    ) -> GeneratedTextType:
        """Draft the prose for one form field from the data already on the form.

        Purely advisory: the caller drops the text into the input, where the user
        edits or discards it. Nothing is saved here.
        """
        require_auth(info)
        ctx = {item.key: item.value for item in (context or [])}
        try:
            text = compose.generate(
                field=field,
                context=ctx,
                instruction=instruction,
                existing=existing,
            )
        except compose.ComposeError as exc:
            raise ValidationError(str(exc)) from exc
        return GeneratedTextType(ok=True, text=text, field=field)
