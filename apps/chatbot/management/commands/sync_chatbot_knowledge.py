from django.core.management.base import BaseCommand

from apps.chatbot.services.knowledge import sync_seed_entries


class Command(BaseCommand):
    help = "Re-sync the built-in assistant knowledge base into the database."

    def handle(self, *args, **options):
        count = sync_seed_entries()
        self.stdout.write(self.style.SUCCESS(f"Synced {count} seed knowledge entries."))
