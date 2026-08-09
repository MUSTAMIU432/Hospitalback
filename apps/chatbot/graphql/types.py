import strawberry


@strawberry.type
class KnowledgeEntryType:
    key: str
    title: str
    body: str
    roles: list[str]
    tags: list[str]
    source: str


@strawberry.type
class ChatbotKnowledgeType:
    """Everything the widget needs to answer locally without a round-trip."""

    role: str
    role_label: str
    entries: list[KnowledgeEntryType]
    suggestions: list[str]
    provider: str
    model: str
    provider_ready: bool
    greeting: str


@strawberry.input
class ChatHistoryInput:
    role: str
    text: str


@strawberry.type
class WorkflowChatReply:
    ok: bool
    answer: str
    provider: str
    model: str
    used_fallback: bool
    """Set only when the user opted in to contribute — needed to rate the answer."""
    interaction_id: str | None
    sources: list[str]
    suggestions: list[str]


@strawberry.type
class ChatOperationResult:
    ok: bool
    message: str
    count: int = 0


@strawberry.input
class ComposeContextInput:
    """One label/value pair of form context, e.g. programme -> "MPH"."""

    key: str
    value: str


@strawberry.type
class GeneratedTextType:
    ok: bool
    text: str
    field: str
