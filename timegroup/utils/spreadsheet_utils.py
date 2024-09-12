import os
import sys
from pathlib import Path
from loguru import logger
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_service():
    creds = None
    token_file = "token.json"
    if getattr(sys, 'frozen', False):
        # If running in a PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # If running in a regular Python environment
        base_path = Path(__file__).resolve().parent
    token_path = os.path.join(base_path, token_file)

    if os.path.exists(token_path):
        logger.debug(f"Credentials found")
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        logger.debug(f"Loaded credentials")
    if not creds or not creds.valid:
        logger.debug(f"Credentials not exists")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file = "credentials.json"
            credentials_path = os.path.join(base_path, credentials_file)
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    logger.debug(f"End of get_service")
    return build("sheets", "v4", credentials=creds)

def read_data(service, spreadsheet_id, range_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    rows = result.get("values", [])
    logger.debug(f"{len(rows)} rows read.")
    return rows

def replace_data(service, spreadsheet_id, range_name, values):
    clear_data(service, spreadsheet_id, range_name)
    body = {
        "values": values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption="RAW", body=body).execute()
    logger.debug(f"{result.get('updatedCells')} cells were replaced.")

def append_data(service, spreadsheet_id, range_name, values):
    body = {
        "values": values
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption="RAW", body=body).execute()
    logger.debug(f"{result.get('updates').get('updatedCells')} cells were appended.")

def clear_data(service, spreadsheet_id, range_name):
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        body={}
    ).execute()
    logger.debug(f"Cleared {range_name}")