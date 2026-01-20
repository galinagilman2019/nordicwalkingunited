from django.core.management.base import BaseCommand
from core.models import User  # Adjust this import path if needed

class Command(BaseCommand):
    help = "Update users with country_user=None to a default value ('US')"

    def handle(self, *args, **options):
        default_country = 'US'
        users_to_update = User.objects.filter(country_user__isnull=True)

        count = users_to_update.count()
        if count == 0:
            self.stdout.write("No users found with country_user=None.")
            return

        for user in users_to_update:
            user.country_user = default_country
            user.save()

        self.stdout.write(f"Updated {count} user(s) to have country_user='{default_country}'.")
