from django.core.management.base import BaseCommand
import sqlite3
class Command(BaseCommand):
    help = "Runs my custom script"

    def handle(self, *args, **kwargs):
        print("Running my script...")
        conn = sqlite3.connect('db.sqlite3')  # Replace 'db.sqlite3' with your database file name

# Create a cursor
        cursor = conn.cursor()

# Execute the query to get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

# Fetch all table names
        tables = cursor.fetchall()

# Print the table names
        for table in tables:
            print(table[0])

# Close the connection
        conn.close()


        self.stdout.write(self.style.SUCCESS("Script executed successfully!"))
