import os
import django
from django.db import connections

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yourproject.settings")  # <-- replace with your settings module
django.setup()

connection = connections["default"]
cursor = connection.cursor()

# Delete all migration history so Django can rebuild fresh
cursor.execute("DELETE FROM django_migrations;")
connection.commit()

print("✅ Cleared migration history table successfully!")
