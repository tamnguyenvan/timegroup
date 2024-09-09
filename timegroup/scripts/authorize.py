import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def authenticate():
    creds = None
    token_file = "token.json"
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    return build("sheets", "v4", credentials=creds)

service = authenticate()

# spreadsheet_id = "1xdjFUj-1FnPjaTdNLpzkqtlJfHC_mGrIZ-WnSAeqMQY"
# spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
# sheets = spreadsheet.get('sheets', [])
# for sheet in sheets:
#     print(sheet['properties']['title'])