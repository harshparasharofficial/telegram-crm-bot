import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Telegram Bot token
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x]  # comma separated Telegram IDs
DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "en")  # en / hi / mix

# Firebase credentials will be passed as JSON string in env var FIREBASE_CREDENTIALS
FIREBASE_CREDENTIALS = os.environ.get("FIREBASE_CREDENTIALS")
FIREBASE_DB_URL = os.environ.get("FIREBASE_DB_URL")  # e.g. https://your-project-default-rtdb.firebaseio.com
