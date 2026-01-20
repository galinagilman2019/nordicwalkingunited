from django.core.management.base import BaseCommand
from core.models import User

class Command(BaseCommand):
    help = 'Deletes all User records from the database'

    def handle(self, *args, **kwargs):
        count = User.objects.count()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} users."))
