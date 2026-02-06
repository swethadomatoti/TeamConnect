import os
import django
from django.db import connections

# 👇 replace this with your actual settings module (check manage.py)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TeamConnect.settings")

django.setup()

connection = connections["default"]
cursor = connection.cursor()

# Clear the migration history table
cursor.execute("DELETE FROM django_migrations;")
connection.commit()

print("✅ Cleared migration history table successfully!")
