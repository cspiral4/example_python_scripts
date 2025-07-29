#!python
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth.transport.requests
import requests
import datetime
import dateutil
import os
import json

# script root and directory
SCRIPT_ROOT = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_ROOT)

# Google client authentication information
# Wolf PAC auth info
GOOGLE_CAL_ID = "your_google_calendar_id@group.calendar.google.com"
SCOPE = ["https://www.googleapis.com/auth/calendar"]

# Used to store the token once captured.
TOKEN_FILE = os.path.join(SCRIPT_DIR, "gcal.json")


# Calendar authentication function.
# Uses the service account json file for credentials.
def open_google_calendar():
    """
    Opens the user's primary Google Calendar using an OAuth 2.0 json
    credentials information in the TOKEN_FILE.

    Returns:
        service or None: the Google service object connected to the
                         WolfPack calendar.
    """
    try:
        # Create credentials object from service account json file.
        info = None
        req = google.auth.transport.requests.Request()
        with open(TOKEN_FILE) as source:
            info = json.load(source)
        creds = service_account.Credentials.from_service_account_info(info)
        # Define the access scope.
        scoped_creds = creds.with_scopes(SCOPE)
        # Make sure there is a valid access token.
        access_token = scoped_creds.token
        if access_token is None:
            scoped_creds.refresh(req)
            access_token = scoped_creds.token
            if access_token is None:
                print("ERROR: unable to obtain Google OAuth2 access token")
                return None

        # Create a session using the credentials by
        # building a network service object.
        service = build('calendar', 'v3', credentials=scoped_creds)
        return service

    except HttpError as error:
        print(f"ERROR: Authentication failed: {error}")
        return None


def create_event(service, event_data):
    """
    Add an event to the google calendar referenced by service

    Parameters:
        service: Google calendar link
        event_data: calendar event data for creating a new
                    google calendar event.

    Returns:
        new_event or None: If successful, returns the newly
                           created Google calendar event
    """

    # check to see if event already exists.
    possible_duplicate = find_event_by_id(service, event_data['event_id'])
    event_id = event_data['event_id']
    ext_prop = f'INFO: event id: {event_id}'
    if possible_duplicate is not None:
        print("INFO: Event already exists in Google calendar, skipping: %s"
              %event_data['summary'])
        return possible_duplicate

    google_data = {
        'summary': event_data['summary'],
        'description': event_data['description'],
        'start': {
            'dateTime': event_data['start'],
            'timeZone': 'America/New_York',  # Adjust to your timezone
        },
        'end': {
            'dateTime': event_data['end'],
            'timeZone': 'America/New_York',  # Adjust to your timezone
        },
        'location': event_data['location'],
        'recurrence': [event_data['recurrence']],
        'extendedProperties': {
            'private': {
                'at_event_id': event_id,
                }
            },
        'attendees': event_data['attendees']
    }

    try:
        new_event = service.events().insert(
            calendarId=GOOGLE_CAL_ID,
            body=google_data
            ).execute()
    except HttpError as err:
        print(f'ERROR: failed to create new event {event_data["summary"]}')
        print(f'{err}')
        exit(1)

    if new_event is None:
        print("ERROR: Unable to create Calendar event\n")
    else:
        print(f'INFO: Event created: {new_event.get("htmlLink")}\n')

    return new_event


def modify_event(service, at_event_data):
    """
    Modify the Google event whose extendedProperties event id
    matches the AirTable event id.

    Parameters:
        service:     Authenticated Google service object
        event_data:  Data to be used for modifying an existing
                     Google Calendar event.

    Returns:
        updated_gcal_event or None: Returns the response from the
                                    modify request or None if the
                                    event is not found in Google.
    """

    gcal_event = find_event_by_id(service, at_event_data['event_id'])
    if gcal_event is None:
        print("INFO: no matching google calendar event for AirTable event id %s"
              %at_event_data['event_id'])
        return None

    gcal_event['summary'] = at_event_data['summary']
    gcal_event['description'] = at_event_data['description']
    gcal_event['start']['dateTime'] = at_event_data['start']
    gcal_event['start']['timeZone'] = 'America/New_York'  # Adjust to your timezone
    gcal_event['end']['dateTime'] = at_event_data['end']
    gcal_event['end']['timeZone'] = 'America/New_York'  # Adjust to your timezone
    gcal_event['location'] = at_event_data['location']
    gcal_event['recurrence'] = [at_event_data['recurrence']]
    gcal_event['extendedProperties'] = f'at_event_id={at_event_data["event_id"]}'
    gcal_event['attendees'] = at_event_data['attendees']

    try:
        updated_gcal_event = service.events().update(
            calendarId=GOOGLE_CAL_ID,
            eventId=gcal_event['eventId'],
            body=gcal_event
            ).execute()
    except HttpError as err:
        print(f'ERROR: unable to update event {at_event_data["summary"]}')
        print(f'{err}')
        return None

    return updated_gcal_event

def delete_event(service, at_event_id):
    """
    Delete the Google Calendar event whose AirTable event id
    matches at_event_id.

    Parameters:
        service:       Google service object connected to calendar
        at_event_id:   The AirTable event id used to find Google
                       calendar event to be deleted.
    Returns:
        deleted_event or None: Response from the delete request or None
                               if the event doesn't exist in Google.
    """
    gcal_event = find_event_by_id(service, at_event_id)
    if gcal_event is None:
        print("INFO: no matching google calendar event for AirTable event id %s"
              %at_event_id)
        return None

    try:
        deleted_event = service.events().delete(
            calendarId=GOOGLE_CAL_ID,
            eventId=gcal_event['eventId']
            ).execute()
    except HttpError as err:
        print(f'ERROR: Unable to delete google calendar event {gcal_event["summary"]}')
        return None

    print("INFO: Deleted Google calendar event %s: %s"
          %(gcal_event['summary'], deleted_event))

    return deleted_event

# As an FYI, this is a method to read the calendar entries
def read_google_events(service):
    """
    Fetch and print next 10 events

    Parameters:
        service:    Google Calendar service link

    Returns:
        cal_events or None: list of Google Calendar events found
    """
    results = service.events().list(
        calendarId=GOOGLE_CAL_ID, maxResults=50
        ).execute()
    cal_events = results.get('items', [])

    if cal_events is None:
        print("WARNING: No Google calendar events found.")
        return None
    else:
        return cal_events

# TBD: add function that takes service, start, and end times
#      to limit the events grabbed.

# Function that returns a list of events with the
# specified summary field value.
def find_event_by_summary(service, summary):
    """
    Finds a Google Calendar event with a matching summary.

    Args:
        service: Authorized Google Calendar API service instance.
        summary: The event summary to search for.

    Returns:
        dict or None: The first event that matches the summary or None if not found.
    """
    event_matches = []

    try:
        events_result = service.events().list(
            calendarId=GOOGLE_CAL_ID,
            maxResults=250
            ).execute()

        events = events_result.get('items', [])

        for event in events:
            if event.get('summary', '').strip().lower() == summary.strip().lower():
                event_matches.append(event)

        if len(event_matches) == 0:  # No match found
            return None

    except Exception as e:
        print(f"ERROR: {e}")
        return None

    return event_matches

# Search Google calendar for an event with the
# specified AirTable event_id.
def find_event_by_id(service, event_id):
    """
    Finds a Google Calendar event with a matching summary.

    Args:
        service:  Authorized Google Calendar API service instance.
        event_id: The AirTable event id to search for in extendedProperties.

    Returns:
        event or None: The first google calendar event that matches the
                       AirTable event id or None if not found.
    """
    event_match = None
    events_result = None

    try:
        events_result = service.events().list(
            calendarId=GOOGLE_CAL_ID,
            maxResults=250
        ).execute()
    except HttpError as e:
        print(f'ERROR: Unable to access google calendar entries: {e}')
        return None
    
    events = events_result.get('items', [])
    num_events = len(events)
    for event in events:
        gcal_ep_priv = ''
        gcal_event_id = ''
        gcal_ext_prop = event.get('extendedProperties', '')
        if len(gcal_ext_prop) > 0:
            gcal_ep_priv = gcal_ext_prop.get('private','')
        if len(gcal_ep_priv) > 0:
            gcal_event_id = gcal_ep_priv.get('at_event_id')

        if event_id == gcal_event_id:
            event_match = event
            break

    return event_match

# Compare AirTable event_data to Google calendar event settings.
def compare_events(at_event_data, gcal_event):
    """
    Compares an at_event_data['event_id'] to the
    gcal_event.get('extendedProperties') value.  Searches for
    event id string in the extendedProperties settings.

    Args:
        at_event_data: dictionary of AirTable event data to use
                       in constructing a goole calendar event
        gcal_event: a google calendar event to compare to the
                    AirTable event data

    Returns:
        True:  at_event_data['event_id'] matches the gcal_event
               'extendedProperties' value.
        False: at_event_id is not in the extendedProperties or is not
               the same.
    """
    matches = True

    # Compare AirTable event ids.
    gcal_ep_priv = ''
    gcal_event_id = ''
    gcal_ext_prop = event.get('extendedProperties', '')
    if len(gcal_ext_prop) > 0:
        gcal_ep_priv = gcal_ext_prop.get('private','')
    if len(gcal_ep_priv) > 0:
        gcal_event_id = gcal_ep_priv.get('at_event_id', '')

    if not at_event_data['event_id'] == gcal_event_id:
        matches = false

    return matches
