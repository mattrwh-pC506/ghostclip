import os
from datetime import timedelta
from .ga import build_service


def set_color_id(rule_set):
    if rule_set.last_transaction_amount < 0:
        color_id = '4'
    else:
        color_id = '9'
    return color_id


def build_body(rule_set):
    return {
        'summary': f'{rule_set.last_transaction_amount} / {rule_set.last_transaction_name}',
        'description': rule_set.last_transaction_name,
        'start': {'date': rule_set.predicted_next_transaction_date.isoformat()},
        'end': {'date': rule_set.predicted_next_transaction_date.isoformat()},
        'colorId': set_color_id(rule_set),
    }


def create_rule_set_event(rule_set):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    service = build_service()
    event = service.events().insert(calendarId=calendar_id,
                                    body=build_body(rule_set)).execute()
    rule_set.calendar_event_id = event['id']
    rule_set.save()


def patch_rule_set_event(rule_set):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    event_id = rule_set.calendar_event_id
    service = build_service()
    event = service.events().patch(calendarId=calendar_id,
                                   eventId=event_id, body=build_body(rule_set)).execute()


def delete_rule_set_event(rule_set):
    calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
    service = build_service()
    service.events().delete(calendarId=calendar_id,
                            eventId=rule_set.calendar_event_id).execute()
