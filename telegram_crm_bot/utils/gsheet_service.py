from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SHEET_NAME = "LeadPilot_CRM_Data"  # change if different

def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("telegram_crm_bot/utils/oauth_credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    service = build('sheets', 'v4', credentials=creds)
    return service

def find_sheet_id(service, sheet_name):
    spreadsheet = service.spreadsheets().get(spreadsheetId=get_spreadsheet_id(service)).execute()
    for sheet in spreadsheet["sheets"]:
        if sheet["properties"]["title"] == sheet_name:
            return sheet["properties"]["sheetId"]
    return None

def get_spreadsheet_id(service):
    spreadsheet_list = service.drive().files().list(q=f"name='{SHEET_NAME}'", fields="files(id)").execute()
    return spreadsheet_list['files'][0]['id']

def append_row(sheet_name, values):
    service = get_service()
    spreadsheet_id = get_spreadsheet_id(service)
    body = {"values": [values]}
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:Z",
        valueInputOption="RAW",
        body=body
    ).execute()

def get_all_records(sheet_name):
    service = get_service()
    spreadsheet_id = get_spreadsheet_id(service)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:Z"
    ).execute()
    values = result.get("values", [])
    if not values:
        return []
    keys = values[0]
    records = [dict(zip(keys, row)) for row in values[1:]]
    return records

def add_user(user_id, name, role="agent", team="", language="en"):
    append_row("Users", [user_id, name, role, team, language])

def get_user(user_id):
    users = get_all_records("Users")
    for u in users:
        if str(u.get("id")) == str(user_id):
            return u
    return None

def add_lead(name, phone, budget, source, created_by):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lead_id = f"LD{int(datetime.now().timestamp())}"
    append_row("Leads", [lead_id, name, phone, budget, source, "New", created_by, created_by, now])
    return lead_id

def get_leads_by_user(user_id):
    leads = get_all_records("Leads")
    return [l for l in leads if str(l.get("assigned_to")) == str(user_id)]

def add_attendance(user_id, action, lat, lon):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.now().strftime("%Y-%m-%d")
    if action == "in":
        append_row("Attendance", [user_id, today, now, "", "", lat, lon])
    else:
        rows = get_all_records("Attendance")
        for i, row in enumerate(rows, start=2):
            if row.get("user_id") == str(user_id) and row.get("date") == today and not row.get("check_out"):
                service = get_service()
                spreadsheet_id = get_spreadsheet_id(service)
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"Attendance!D{i}",
                    valueInputOption="RAW",
                    body={"values": [[now]]}
                ).execute()
                return True
    return False
