import os
from pathlib import Path
from loguru import logger
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_service():
    creds = None
    token_file = "token.json"
    token_path = Path(__file__).parent / token_file
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
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