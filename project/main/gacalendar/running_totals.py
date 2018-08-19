import os
from datetime import timedelta
from .ga import build_service


def build_body(running_total):
    return {
        'summary': f'{running_total.amount} / {running_total.target}',
        'description': f'Running total for week starting in {running_total.start_date.isoformat()} and ending in {running_total.end_date.isoformat()}',
        'start': {'date': running_total.start_date.isoformat()},
        'end': {'date': (running_total.end_date + timedelta(days=1)).isoformat()},
        'colorId': '1',
    }


def create_running_total_event(running_total):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    service = build_service()
    event = service.events().insert(calendarId=calendar_id,
                                    body=build_body(running_total)).execute()
    running_total.calendar_event_id = event['id']
    running_total.save()


def patch_running_total_event(running_total):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    event_id = running_total.calendar_event_id
    service = build_service()
    event = service.events().patch(calendarId=calendar_id,
                                   eventId=event_id, body=build_body(running_total)).execute()


def delete_running_total_event(running_total):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    service = build_service()
    service.events().delete(calendarId=calendar_id,
                            eventId=running_total.calendar_event_id).execute()
