from django.core.management.base import BaseCommand
from core.models import Submission

class Command(BaseCommand):
    help = 'Deletes all User records from the database'

    def handle(self, *args, **kwargs):
        count = Submission.objects.count()
        Submission.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} Submissions."))
