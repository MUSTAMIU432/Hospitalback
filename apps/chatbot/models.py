import uuid

from django.conf import settings
from django.db import models


class KnowledgeSource(models.TextChoices):
    SEED = "seed", "Built-in"
    LEARNED = "learned", "Learned from chat"
    MANUAL = "manual", "Added by admin"


class KnowledgeEntry(models.Model):
    """One answerable fact about the platform.

    Seed entries ship with the code and are re-synced on every deploy; learned
    entries come from conversations users chose to contribute and stay inactive
    until an admin approves them.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=200)
    body = models.TextField()
    # Empty = applies to every role. Stored comma-separated to keep the schema
    # sqlite-friendly and easy to edit in the Django admin.
    roles = models.CharField(
        max_length=300,
        blank=True,
        default="",
        help_text="Comma-separated roles this applies to. Blank = all roles.",
    )
    tags = models.CharField(
        max_length=400,
        blank=True,
        default="",
        help_text="Comma-separated keywords used for retrieval.",
    )
    source = models.CharField(max_length=20, choices=KnowledgeSource.choices, default=KnowledgeSource.SEED)
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive entries are never sent to the assistant or the frontend.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chatbot_knowledge_entries"
        ordering = ["title"]
        verbose_name = "knowledge entry"
        verbose_name_plural = "knowledge entries"
        indexes = [models.Index(fields=["is_active", "source"])]

    def __str__(self) -> str:
        return self.title

    @property
    def role_list(self) -> list[str]:
        return [r.strip() for r in self.roles.split(",") if r.strip()]

    @property
    def tag_list(self) -> list[str]:
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    def applies_to(self, role: str) -> bool:
        roles = self.role_list
        return not roles or role in roles


class ChatInteraction(models.Model):
    """A question/answer pair kept only when the user opted in to contribute.

    Ratings drive what gets promoted into the knowledge base, and the user can
    wipe their own rows at any time from the chat settings panel.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_interactions",
    )
    role = models.CharField(max_length=40, blank=True, default="")
    question = models.TextField()
    answer = models.TextField()
    provider = models.CharField(max_length=40, blank=True, default="")
    model = models.CharField(max_length=80, blank=True, default="")
    used_fallback = models.BooleanField(default=False)
    matched_keys = models.CharField(
        max_length=400,
        blank=True,
        default="",
        help_text="Knowledge entry keys retrieved for this answer.",
    )
    helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="User rating: true = helpful, false = not helpful, null = unrated.",
    )
    promoted_entry = models.ForeignKey(
        KnowledgeEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="learned_from",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chatbot_interactions"
        ordering = ["-created_at"]
        verbose_name = "chat interaction"
        verbose_name_plural = "chat interactions"
        indexes = [models.Index(fields=["user", "created_at"])]

    def __str__(self) -> str:
        return self.question[:60]
