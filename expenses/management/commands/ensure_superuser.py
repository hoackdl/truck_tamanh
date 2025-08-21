# expenses/commands/ensure_superuser.py


from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Ensure a Django superuser exists, creating it if necessary."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Admin123!")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"✅ Superuser '{username}' created."))
        else:
            self.stdout.write(self.style.WARNING(f"ℹ️ Superuser '{username}' already exists."))
