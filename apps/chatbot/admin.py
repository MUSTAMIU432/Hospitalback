from django.contrib import admin

from apps.chatbot.models import ChatInteraction, KnowledgeEntry


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "key", "source", "roles", "is_active", "updated_at")
    list_filter = ("source", "is_active")
    search_fields = ("key", "title", "body", "tags")
    ordering = ("-updated_at",)
    actions = ["approve_entries", "deactivate_entries"]

    @admin.action(description="Approve — start serving these answers")
    def approve_entries(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} entry(ies) activated.")

    @admin.action(description="Deactivate — stop serving these answers")
    def deactivate_entries(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} entry(ies) deactivated.")


@admin.register(ChatInteraction)
class ChatInteractionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "role", "question", "helpful", "used_fallback")
    list_filter = ("helpful", "used_fallback", "role")
    search_fields = ("question", "answer")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
