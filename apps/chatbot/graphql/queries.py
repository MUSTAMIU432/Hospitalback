import strawberry
from django.conf import settings
from strawberry.types import Info

from apps.chatbot.graphql.types import ChatbotKnowledgeType, KnowledgeEntryType
from apps.chatbot.services import knowledge as kb
from apps.chatbot.services import provider
from apps.chatbot.services.roles import chat_role_for
from apps.users.graphql.auth import require_auth


@strawberry.type
class ChatbotQuery:
    @strawberry.field
    def chatbot_knowledge(self, info: Info) -> ChatbotKnowledgeType:
        """The role-filtered knowledge base, cached client-side for local answers."""
        user = require_auth(info)
        role = chat_role_for(user)
        first_name = (getattr(user, "first_name", "") or "").strip() or "there"
        label = kb.ROLE_LABELS.get(role, role.replace("_", " ").title())
        return ChatbotKnowledgeType(
            role=role,
            role_label=label,
            entries=[
                KnowledgeEntryType(
                    key=e.key,
                    title=e.title,
                    body=e.body,
                    roles=e.role_list,
                    tags=e.tag_list,
                    source=e.source,
                )
                for e in kb.entries_for_role(role)
            ],
            suggestions=kb.suggestions_for(role),
            provider=(getattr(settings, "CHATBOT_PROVIDER", "") or ""),
            model=(getattr(settings, "CHATBOT_MODEL", "") or ""),
            provider_ready=provider.is_configured(),
            greeting=(
                f"Hello {first_name}. I'm the support assistant for the {label} workspace. "
                "Ask me how anything in this platform works and I'll answer from what's configured here."
            ),
        )
