import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.accounts.models import User
from apps.community.models import Community
from apps.locations.models import Location
from django.db import transaction

@transaction.atomic
def seed_data():
    # Keep it simple, just create superadmin if it doesn't exist
    if not User.objects.filter(email='admin@example.com').exists():
        User.objects.create_superuser(
            email='admin@example.com',
            password='Password123!',
            name='Super Admin'
        )
        print("Superuser created: admin@example.com / Password123!")
    else:
        print("Superuser already exists.")

if __name__ == '__main__':
    seed_data()
