import os
from datetime import timedelta
import datetime
import pytz
import httplib2
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

def build_service():
    filename = 'main/gacreds.json'
    scopes = ['https://www.googleapis.com/auth/calendar']
    credentials = service_account.Credentials.from_service_account_file(filename, scopes=scopes)
    service = build('calendar', 'v3', credentials=credentials)
    return service

def set_summary(transaction):
    if transaction.pending:
        summary = f'(Pending) {transaction.amount} / {transaction.name}'
    else:
        summary = f'{transaction.amount} / {transaction.name}'
    return summary

def set_color_id(transaction):
    if transaction.amount < 0:
        color_id = '11'
    else:
        color_id = '10'
    return color_id

def create_transaction_event(transaction):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    service = build_service()

    summary = set_summary(transaction)
    color_id = set_color_id(transaction)
    body = {
            'summary': summary,
            'description': transaction.name,
            'start': {'date': transaction.date.isoformat()},
            'end': {'date': (transaction.date + timedelta(minutes=15)).isoformat()},
            'colorId': color_id,
            }

    event = service.events().insert(calendarId=calendar_id, body=body).execute()

    transaction.calendar_event_id = event['id']
    transaction.save()

def patch_transaction_event(transaction):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    event_id = transaction.calendar_event_id
    service = build_service()

    summary = set_summary(transaction)
    color_id = set_color_id(transaction)
    body = {
            'summary': summary,
            'description': transaction.name,
            'start': {'date': transaction.date.isoformat()},
            'end': {'date': (transaction.date + timedelta(minutes=15)).isoformat()},
            'colorId': color_id,
            }

    event = service.events().patch(calendarId=calendar_id, eventId=event_id, body=body).execute()

def delete_transaction_event(transaction):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    service = build_service()
    service.events().delete(calendarId=calendar_id, eventId=transaction.calendar_event_id).execute()
