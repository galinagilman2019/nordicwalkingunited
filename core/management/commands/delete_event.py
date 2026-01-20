from django.core.management.base import BaseCommand
from core.models import Event

class Command(BaseCommand):
    help = 'Deletes all User records from the database'

    def handle(self, *args, **kwargs):
        count = Event.objects.count()
        Event.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} events."))
