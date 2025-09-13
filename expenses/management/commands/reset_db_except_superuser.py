# your_app/management/commands/reset_db_sqlite.py
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Reset DB SQLite, migrate sạch, giữ superuser"

    def handle(self, *args, **kwargs):
        db_path = "db.sqlite3"
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write("🗑️  Deleted SQLite DB file")

        # Xóa migration cũ
        for app in ["expenses"]:  # thêm app khác nếu muốn
            migrations_path = f"{app}/migrations"
            for f in os.listdir(migrations_path):
                if f != "__init__.py" and f.endswith(".py"):
                    os.remove(os.path.join(migrations_path, f))
            self.stdout.write(f"🗑️  Cleared migrations for app {app}")

        # Migrate sạch
        call_command("makemigrations")
        call_command("migrate", "--noinput")

        # Tạo superuser nếu chưa có
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="Admin123!"
            )
            self.stdout.write("✅ Superuser created")
        else:
            self.stdout.write("ℹ️ Superuser already exists")
