import os
from datetime import timedelta
import datetime
from .ga import build_service


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


def build_body(transaction):
    return {
        'summary': set_summary(transaction),
        'description': transaction.name,
        'start': {'date': transaction.date.isoformat()},
        'end': {'date': transaction.date.isoformat()},
        'colorId': set_color_id(transaction),
    }


def create_transaction_event(transaction):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    service = build_service()
    event = service.events().insert(calendarId=calendar_id,
                                    body=build_body(transaction)).execute()
    transaction.calendar_event_id = event['id']
    transaction.save()


def patch_transaction_event(transaction):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    event_id = transaction.calendar_event_id
    service = build_service()
    event = service.events().patch(calendarId=calendar_id,
                                   eventId=event_id, body=build_body(transaction)).execute()


def delete_transaction_event(transaction):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    service = build_service()
    service.events().delete(calendarId=calendar_id,
                            eventId=transaction.calendar_event_id).execute()
