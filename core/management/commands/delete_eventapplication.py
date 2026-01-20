from django.core.management.base import BaseCommand
from organize.models import EventApplication

class Command(BaseCommand):
    help = 'Deletes all User records from the database'

    def handle(self, *args, **kwargs):
        count = EventApplication.objects.count()
        EventApplication.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} EventApplications."))
