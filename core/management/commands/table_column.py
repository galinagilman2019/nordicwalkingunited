from django.core.management.base import BaseCommand
import sqlite3

class Command(BaseCommand):
    help = "Runs my custom script"

    def handle(self, *args, **kwargs):
        print("Running my script...")
        DB_PATH = "db.sqlite3"

        def get_table_columns(table_name):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [row[1] for row in cursor.fetchall()]  # Extract column names

            cursor.close()
            conn.close()

            return columns

# Get column names for all this tables
        print("core_submission:", get_table_columns("core_submission"))
        print("core_user:", get_table_columns("core_user"))
        print("core_event:", get_table_columns("core_event"))
        print("core_submission:", get_table_columns("core_submission"))
        print("core_event_participants columns:", get_table_columns("core_event_participants"))


        self.stdout.write(self.style.SUCCESS("Script executed successfully!"))

