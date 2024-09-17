import os
import sys
from pathlib import Path
from loguru import logger
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_service():
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    service_account_file = os.path.join(base_path, "service_account.json")
    logger.debug(f"Path to service account: {service_account_file}")

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES)

    return build("sheets", "v4", credentials=credentials)

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