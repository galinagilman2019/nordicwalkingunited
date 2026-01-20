import pandas as pd
from django.core.management.base import BaseCommand
from organize.models import Event
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = "Import Event data from Excel or CSV"

    def add_arguments(self, parser):
        parser.add_argument("filepath", type=str, help="Path to Excel or CSV file")

    def handle(self, *args, **options):
        filepath = options["filepath"]

        try:
            if filepath.endswith(".xlsx") or filepath.endswith(".xls"):
                df = pd.read_excel(filepath)
            elif filepath.endswith(".csv"):
                df = pd.read_csv(filepath)
            else:
                self.stderr.write("Unsupported file format.")
                return
        except Exception as e:
            self.stderr.write(f"Error reading file: {e}")
            return

        success_count = 0
        for i, row in df.iterrows():
            try:
                event = Event.objects.create(
                    name=row["name"],
                    city=row["city"],
                    country=row["country"],
                    nwgroup=row["nwgroup"],
                    preview=row.get("preview", ""),
                    start_time=row.get("start_time"),
                    duration=row.get("duration"),
                    difficulty=row.get("difficulty", 0),
                    unit=row.get("unit", 0),
                    distance=row.get("distance"),
                    latlng=row.get("latlng"),
                    uuuid=row["uuuid"],
                )

                # Handle participants (comma-separated emails or IDs)
                participants = row.get("participants")
                if participants and isinstance(participants, str):
                    for part in participants.split(","):
                        part = part.strip()
                        try:
                            user = User.objects.get(email=part)
                            event.participants.add(user)
                        except User.DoesNotExist:
                            self.stderr.write(f"Participant user not found: {part}")

                # Handle team (comma-separated emails or IDs)
                team = row.get("team")
                if team and isinstance(team, str):
                    for member in team.split(","):
                        member = member.strip()
                        try:
                            user = User.objects.get(email=member)
                            event.team.add(user)
                        except User.DoesNotExist:
                            self.stderr.write(f"Team user not found: {member}")

                success_count += 1
                self.stdout.write(f"Imported event: {event.name}")
            except IntegrityError as e:
                self.stderr.write(f"IntegrityError on row {i}: {e}")
            except KeyError as e:
                self.stderr.write(f"Missing required field {e} in row {i}")
            except Exception as e:
                self.stderr.write(f"Unexpected error in row {i}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Imported {success_count} events."))







"""
import pandas as pd
from django.core.management.base import BaseCommand
from organize.models import Event  # replace with your model
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
                Event.objects.create(
                    name=row["name"],
                    date=row["date"],
                    city=row["city"],
                    country=row["country"],
                    nwgroup=row["nwgroup"],
                    preview=row["preview"],
                    participants=row["participants"],
                    start_time=row["start_time"],
                    duration=row["duration"],
                    difficulty=row["difficulty"],
                    unit=row["unit"],
                    distance=row["distance"],
                    latlng=row["latlng"],
                    email=row["email"],

                    team=row["team"],
                    is_on_homepage=row["is_on_homepage"],
                    is_deleted=row["is_deleted"],
                    is_page_live=row["is_page_live"],
                    is_frozen=row["is_frozen"],
                    uuuid=row["uuuid"],
                )
                self.stdout.write(f"Imported: {row['main_organizer']}")

            except IntegrityError:
                self.stderr.write(f"Duplicate or error on row: {row.to_dict()}")
            except KeyError as e:
                self.stderr.write(f"Missing column: {e}")
"""

