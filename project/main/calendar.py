import os
from datetime import timedelta
import datetime
import pytz
import httplib2
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

def build_service():
    filename = 'gacreds.json'
    scopes = ['https://www.googleapis.com/auth/calendar']
    credentials = service_account.Credentials.from_service_account_file(filename, scopes=scopes)
    service = build('calendar', 'v3', credentials=credentials)
    return service

def create_transaction_event(email, transaction):
    service = build_service()

    start_datetime = datetime.datetime.now(tz=pytz.utc)
    event = service.events().insert(calendarId=email, body={
        'summary': 'Foo',
        'description': 'Bar',
        'start': {'dateTime': start_datetime.isoformat()},
        'end': {'dateTime': (start_datetime + timedelta(minutes=15)).isoformat()},
        }).execute()

    print(event)
