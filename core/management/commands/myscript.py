from django.core.management.base import BaseCommand
import sqlite3

class Command(BaseCommand):
    help = "Runs my custom script"
    def handle(self, *args, **kwargs):
        print("Running my script...")
        DB_PATH = "db.sqlite3"

        try:
    # Connect to the SQLite database
            conn = sqlite3.connect(DB_PATH)

    # Create a cursor object
            cursor = conn.cursor()

    # Execute an SQL query
            cursor.execute("SELECT * FROM core_event where city='Manta';")

    # Fetch all results
            records = cursor.fetchall()

    # Print the data
            for row in records:
                print(row)  # Each row is a tuple

    # Close the cursor and connection
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM core_event_team;")
            records = cursor.fetchall()
            for row in records:
                print(row)  # Each row is a tuple
    # Close the cursor and connection
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM organize_eventapplication;")
            records = cursor.fetchall()
            for row in records:
                print(row)  # Each row is a tuple
    # Close the cursor and connection
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM organize_coorganizer;")
            records = cursor.fetchall()
            for row in records:
                print(row)  # Each row is a tuple
     # Close the cursor and connection
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM core_event_participants;")
            records = cursor.fetchall()
            for row in records:
                print(row)  # Each row is a tuple
            cursor.close()
            conn.close()

        except Exception as e:
            print("Error:", e)
        self.stdout.write(self.style.SUCCESS("Script executed successfully!"))




