# notifications/apps.py
from django.apps import AppConfig
from decouple import config
import firebase_admin
from firebase_admin import credentials
from pathlib import Path
from dotenv import load_dotenv

# CORRECT BASE_DIR: folder containing manage.py
BASE_DIR = Path(__file__).resolve().parent.parent  # → /Users/.../fcm_project

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"

    def ready(self):
        if firebase_admin._apps:
            return

        try:
            firebase_path = config("FIREBASE_CREDENTIALS")
            full_path = (BASE_DIR / firebase_path.replace("./", "")).resolve()
            print(f"Looking for Firebase file at: {full_path}")

            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {full_path}")

            cred = credentials.Certificate(str(full_path))
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully!")

        except Exception as e:
            print(f"Firebase init failed: {e}")