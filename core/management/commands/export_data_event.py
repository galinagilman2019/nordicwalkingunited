import pandas as pd
from django.core.management.base import BaseCommand
from organize.models import Event

class Command(BaseCommand):
    help = "Export data from the EventApplication model to an Excel (.xlsx) or CSV (.csv) file"

    def add_arguments(self, parser):
        parser.add_argument("output_path", type=str, help="Path to save the exported file")

    def handle(self, *args, **options):
        output_path = options["output_path"]

        # Query all records
        queryset = Event.objects.all()

        # Convert queryset to a list of dicts
        data = list(queryset.values(
            "name",
            "date",
            "city",
            "country",
            "nwgroup",
            "preview",
            "participants",
            "start_time",
            "duration",
            "difficulty",
            "unit",
            "distance",
            "latlng",
            "email",
            "main_organizer",
            "team",
            "is_on_homepage",
            "is_deleted",
            "is_page_live",
            "is_frozen",
            "attendees_count",
            "applicants_count",
            "uuuid",
        ))

        if not data:
            self.stdout.write("No records found.")
            return

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Export to correct format
        if output_path.endswith(".xlsx") or output_path.endswith(".xls"):
            df.to_excel(output_path, index=False)
        elif output_path.endswith(".csv"):
            df.to_csv(output_path, index=False)
        else:
            self.stderr.write("Unsupported file format. Use .xlsx, .xls, or .csv")
            return

        self.stdout.write(self.style.SUCCESS(f"Exported {len(data)} records to {output_path}"))





