import json
from googleapiclient.discovery import build
from google.oauth2 import service_account


def build_service():
    filename = 'main/gacreds.json'
    scopes = ['https://www.googleapis.com/auth/calendar']
    credentials = service_account.Credentials.from_service_account_file(
        filename, scopes=scopes)
    service = build('calendar', 'v3', credentials=credentials)
    return service
