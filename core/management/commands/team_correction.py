from django.core.management.base import BaseCommand
import sqlite3

class Command(BaseCommand):
    help = "Find missing event records in core_event_team and insert them"

    def handle(self, *args, **kwargs):
        print("Running the script...")
        DB_PATH = "db.sqlite3"

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get all EventIDs from core_event
            cursor.execute("SELECT EventID, UserID FROM core_event;")
            event_records = cursor.fetchall()

            # Get all EventIDs from core_event_team
            cursor.execute("SELECT EventID FROM core_event_team;")
            team_event_ids = {row[0] for row in cursor.fetchall()}  # Using a set for fast lookup

            new_records = []  # To store records that need to be inserted

            for event_id, user_id in event_records:
                if event_id not in team_event_ids:
                    print(f"Missing EventID {event_id} in core_event_team. Adding record.")
                    new_records.append((event_id, user_id))

            # Insert missing records into core_event_team
            for event_id, user_id in new_records:
                cursor.execute("INSERT INTO core_event_team (EventID, UserID) VALUES (?, ?);", (event_id, user_id))

            # Commit changes
            conn.commit()

            print(f"Inserted {len(new_records)} missing records into core_event_team.")

            # Close connection
            cursor.close()
            conn.close()

        except Exception as e:
            print("Error:", e)

        self.stdout.write(self.style.SUCCESS("Script executed successfully!"))