import os
import json
import tempfile
import firebase_admin
from firebase_admin import credentials, db

from config import FIREBASE_CREDENTIALS, FIREBASE_DB_URL

def init_firebase():
    if not FIREBASE_CREDENTIALS or not FIREBASE_DB_URL:
        raise RuntimeError("Set FIREBASE_CREDENTIALS and FIREBASE_DB_URL in environment variables.")

    # Write credentials to a temp file (Railway friendly)
    cred_json = FIREBASE_CREDENTIALS
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        f.write(cred_json)

    cred = credentials.Certificate(path)
    # Initialize only once
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DB_URL
        })

    # Root reference
    root = db.reference("/")
    return root

# Initialize at import time
ROOT_DB = init_firebase()
USERS_REF = ROOT_DB.child("users")
LEADS_REF = ROOT_DB.child("leads")
ATTENDANCE_REF = ROOT_DB.child("attendance")
TASKS_REF = ROOT_DB.child("tasks")
ACTIVITY_LOG_REF = ROOT_DB.child("activity_logs")
