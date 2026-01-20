import pandas as pd
from django.core.management.base import BaseCommand
from organize.models import EventApplication  # replace with your model
from django.db import IntegrityError

import sqlite3

class Command(BaseCommand):
    help = "Import data from Excel or CSV into MySQL database"

    def add_arguments(self, parser):
        parser.add_argument("filepath", type=str, help="Path to Excel or CSV file")

    def handle(self, *args, **options):
        filepath = options["filepath"]

        if filepath.endswith(".xlsx") or filepath.endswith(".xls"):
            df = pd.read_excel(filepath)
        elif filepath.endswith(".csv"):
            df = pd.read_csv(filepath)
        else:
            self.stderr.write("Unsupported file format.")
            return

        for i, row in df.iterrows():
            try:
                EventApplication.objects.create(
                    nwgroup=row["nwgroup"],  # change fields as needed
                    city=row["city"],
                    country=row["country"],
                    main_organizer_email=row["main_organizer_email"],
                    main_organizer_first_name=row["main_organizer_first_name"],
                    status=row["status"],
                )
                self.stdout.write(f"Imported: {row['nwgroup']}")
            except IntegrityError:
                self.stderr.write(f"Duplicate or error on row: {row.to_dict()}")
            except KeyError as e:
                self.stderr.write(f"Missing column: {e}")


