from flask import Flask, redirect, request, url_for
import requests
import threading
import webbrowser
from gevent.pywsgi import WSGIServer
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
import dateutil

# Google client authentication information
# Replace CLIENT_ID, CALENDAR_ID, and CLIENT_SECRET with the actual values
# of the account to be used.
# OAuth2 info for Google authentication
GOOGLE_CLIENT_ID = "CLIENT_ID"
GOOGLE_CAL_ID = "CALENDAR_ID"
GOOGLE_CLIENT_SECRET = "CLIENT_SECRET"
REDIRECT_URI = "http://localhost:5000/callback"
SCOPE = "https://www.googleapis.com/auth/calendar"

# Initialize environment for web service.
app = Flask(__name__)

# Used to store the token once captured.
auth_token_data = {}

# Authentication functions, using Flask to create a web server process.

# Defines the default URI used when the server starts the Flask app.
# This acts as the index.html file of a web site.
@app.route("/")
def index():
    """
    Defines the index.html behavior and defines client information, 
    limits on google data that can be read, and the redirect URI.
    """
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
        "&access_type=offline"
        "&prompt=consent"
    )
    return redirect(auth_url)

# callback grabs the google auth token and returns token_info to start_auth_flow.
@app.route("/callback")
def callback():
    """
    Handles the google authentication request and assigns the token info to
    auth_token_data object.
    """
    code = request.args.get("code")
    if not code:
        return "Authorization failed or denied."

    # Exchange code for token.
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
    if response is None:
        print("ERROR: Unable to obtain google auth response")
        return "Token not obtained"
    token_info = response.json()
    auth_token_data.update(token_info)

    return f"Token received! You may close this window. Access Token: {token_info.get('access_token')}"

# Starts a web service using the defined Flask app index and callback.
def run_flask_app():
    """
    Start up the temporary web service using the Flask app site definitions.
    NOTE: service terminated when the script is terminated.
    """
    http_server = WSGIServer(('localhost',5000), app)
    http_server.serve_forever()

# Start the web server and wait for the authentication token.
def start_auth_flow():
    """
    Start up the temporary web service/flask app in a separate thread, then wait for 
    the callback to update auth_token_data.
    """
    web_thread = threading.Thread(target=run_flask_app, daemon=True)
    if web_thread is None:
        print("ERROR: unable to start web server thread")
        return None
    else:
        web_thread.start()

    print("INFO: opening browser")
    webbrowser.open("http://localhost:5000")
    print("INFO: browser opened")

    # Wait until token is captured
    while "access_token" not in auth_token_data:
        pass  # You can use a better wait mechanism if needed

    return auth_token_data


# Calendar read function.
# Uses the token_data info returned by start_auth_flow()
def open_google_calendar(access_token):
    """
    Opens the user's primary Google Calendar using an OAuth 2.0 token.

    Parameters:
    - access_token (str): A valid OAuth 2.0 access token for Google Calendar API.

    Returns:
    - service: the Google calendar service object connected to a calendar.
    """
    try:
        # Create credentials object from access token
        creds = Credentials(token=access_token)

        # Build the calendar API service
        service = build('calendar', 'v3', credentials=creds)
        return service

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def get_day_of_week(date_string):
    """
    Determines the day of the week from a date string.

    Parameters:
        date_string (str): The date string in the specified format.

    Returns:
        str: The name of the day of the week (e.g., "Monday").
    """
    date = date_string.split('T')
    date_object = datetime.datetime.strptime(date[0], "%Y-%m-%d").date()
    day_of_week_number = date_object.weekday()  # Sunday is 0, Saturday is 6
    days = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]
    return days[day_of_week_number]

def create_event(service, event_data):
    """
    Add an event to the google calendar referenced by service

    Parameters:
    - service: Google calendar link
    - event_data: calendar event data for creating a new
      google calendar event.
    """

    # FREQ rule for the Google calendar event needs extra
    # work if recurrence is monthly.
    # Repeat on first dayX of each month.
    rrules = None
    recur = event_data['recurrence']
    if not event_data['recurrence'] == 'MONTHLY':
        rrules = f'RRULE:FREQ={recur}'
    else:
        rrules = construct_monthly_recurrence(event_data)

    print("\n\nNext Event: %s\n"%event_data['summary'])
    # check to see if event already exists.
    possible_duplicates = find_event_by_summary(service, event_data['summary'])
    if not possible_duplicates is None:
        print("%s possible duplicates found"%len(possible_duplicates))
        for possible_duplicate in possible_duplicates:
            event_match = compare_events(event_data, possible_duplicate)
            if event_match:
                print("Calendar event already exists")
                return possible_duplicate
    else:
        print("No similar events found in the Google Calendar")

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
        'recurrence': [rrules],
        'extendedProperties': f'at_event_id={event_data["event_id"]}'
    }
    new_event = service.events().insert(
        calendarId=GOOGLE_CAL_ID,
        body=google_data
        ).execute()
    if new_event is None:
        print("ERROR: Unable to create Calendar event")
        return None
    else:
        print(f'Event created: {new_event.get("htmlLink")}')
        return new_event

# As an FYI, this is a method to read the calendar entries
def read_google_events(service):
    """
    Fetch and print next 10 events

    Parameters:
    - service:    Google Calendar service link

    Returns:
    - cal_events: list of Google Calendar events
    """
    results = service.events().list(
        calendarId=GOOGLE_CAL_ID, maxResults=10
    ).execute()
    cal_events = results.get('items', [])

    if cal_events is None:
        print("No upcoming events found.")
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
        print(f"An error occurred: {e}")
        return None

    return event_matches

# Compare AirTable event_data to Google calendar event settings.
def compare_events(at_event_data, gcal_event):
    """
    Compares an at_event_data['event_id'] to the
    gcal_event.get('extendedProperties') value.  Searches for

        at_event_id={at_event_data['event_id']}

    in the extendedProperties settings.

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
    if not at_event_data['event_id'] in gcal_event.get('extendedProperties', ''):
        print("AirTable Event ID:  %s"%at_event_data['event_id'])
        print("GoogleCal Props Event ID: %s"%gcal_event.get('extendedProperties', ''))
        matches = False
    else:
        print("The AirTable event with ID %s already exists in the Google Calendar"%at_event_data['summary'])

    print("\n\n")
    return matches

# Update gcal_event with the at_event_data.        
def modify_event(service, at_event_data, gcal_event):
    """
    Modify the Google Calendar event.

    Parameters:
    - service: Google Calendar API service instance
    - at_event_data: Updated event information from AirTable
    - gcal_event: Google Calendar event object to update

    Returns:
    - updated_event: The updated event object
    """
    # Modify the gcal event fields.
    gcal_event['description'] = at_event_data['description']
    gcal_event['start'] = at_event_data['start']
    gcal_event['end'] = at_event_data['end']
    gcal_event['recurrence'] = "RRULE:FREQ=" + at_event_data['recurrence']
    if at_event_data['recurrence'] == 'MONTHLY':
        gcal_event['recurrence'] = construct_monthly_recurrence(at_event_data)

    updated_event = service.events().update(GOOGLE_CAL_ID, gcal_event['id'], gcal_event).execute()

    print(f"Google Event updated: {updated_event.get('htmlLink')}")
    return updated_event

# Construct a Monthly recurrence rule from AirTable data.
def construct_monthly_recurrence(at_event_data):
    """
    Using the start time, get the day of the week
    and week of the month, and construct a monthly
    recurrence rule on a specific day of the week.

    Parameters:
    - at_event_data: AirTable calendar event data

    Returns:
    - recurrence_rule: string containing a monthly recurrence rule.
    """
    recurrence_rule = ''

    # get start date.
    start_date = event_data['start']
    day_of_week = get_day_of_week(start_date)
    week = '1'
    date_time = start_date.split('T')
    date_list = date_time[0].split('-')
    day_of_month = int(date_list[2])
    # get week of the month
    if day_of_month > 28:
        week = '5'
    if day_of_month <= 28 and day_of_month > 21:
        week = '4'
    elif day_of_month <= 21 and day_of_month > 14:
        week = '3'
    elif day_of_month <= 14 and day_of_month > 7:
        week = '2'
    recurrence_rule = f'RRULE:FREQ=MONTHLY;BYDAY={week}{day_of_week}'

    return recurrence_rule
