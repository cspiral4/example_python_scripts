from flask import Flask, redirect, request, url_for
import requests
import threading
import webbrowser
from gevent.pywsgi import WSGIServer
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime

# Google client authentication information
# Replace CLIENT_ID and CLIENT_SECRET with the actual values
# of the account to be used.
GOOGLE_CLIENT_ID = "CLIENT_ID"
GOOGLE_CLIENT_SECRET = "CLIENT_SECRET"
REDIRECT_URI = "http://localhost:5000/callback"
SCOPE = "https://www.googleapis.com/auth/calendar"

# Initialize environment for web service.
app = Flask(__name__)

# Used to store the token once captured.
auth_token_data = {}

#
# Authentication functions, using Flask to create a web server process.
#
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

#
# Calendar functions.
#
# Start a google service that talks to the user's Calendar
# Uses the token_data info returned by start_auth_flow()
def open_google_calendar(access_token: str):
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

# The day of the week is needed for calendar events
# that recur on a particular week day, like second
# Tuesday of every month.  This uses the start date
# to determine the weekday.
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
    day_of_week = None
    if event_data['recurrence'] == 'MONTHLY':
        # get start date.
        start_date = event_data['start']
        day_of_week = get_day_of_week(start_date)
    recur = event_data['recurrence']
    if not event_data['recurrence'] == 'MONTHLY':
        rrules = f'RRULE:FREQ={recur}'
    else:
        # default is the first day_of_week in the month
        # Use the day of the month to determine if
        # using the 2nd, 3rd, 4th, or 5th day_of_week
        # in the month.
        # Not sure how well this will work for all scenarios.
        week = '1'
        date_list = start_date.split('-')
        day_of_month = int(date_list[2])
        if day_of_month > 28:
            week = '5'
        if day_of_month <= 28 and day_of_month > 21:
            week = '4'
        elif day_of_month <= 21 and day_of_month > 14:
            week = '3'
        elif day_of_month <= 14 and day_of_month > 7:
            week = '2'
        rrules = f'RRULE:FREQ=MONTHLY;BYDAY={week}{day_of_week}'

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
        'attendees': [event_data['attendees']],
        'location': event_data['location'],
        'recurrence': [rrules],
    }
    new_event = service.events().insert(
        calendarId='c_ad09f0b2ef528685c282a582162540f025a7bdd5c316b4dc2b1708a6f2a45271@group.calendar.google.com',
        body=google_data
        ).execute()
    if new_event is None:
        print("ERROR: Unable to create Calendar event")
        return None
    else:
        print(f'Event created: {new_event.get("htmlLink")}')
        return new_event

# As an FYI, this is a method to read the calendar entries
# TBD: add start and end times to input argument list
#      to limit the events grabbed.
def read_google_events(service):
    """
    Fetch and print next 10 events

    Parameters:
    - service:    Google Calendar service link

    Returns:
    - cal_events: list of Google Calendar events
    """
    results = service.events().list(
        calendarId='primary', maxResults=10,
        singleEvents=True, orderBy='startTime'
    ).execute()
    cal_events = results.get('items', [])

    if cal_events is None:
        print("No upcoming events found.")
        return None
    else:
        return cal_events
