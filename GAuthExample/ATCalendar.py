#!python
#
# Make sure modules are installed first:
#
# python -m pip install flask gevent google google-api-python-client
#
from flask import Flask, redirect, request, url_for
import requests
import threading
import webbrowser
from gevent.pywsgi import WSGIServer
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime

app = Flask(__name__)

# Google client authentication information
# Replace CLIENT_ID and CLIENT_SECRET with the actual values
# of the account to be used.
CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"
REDIRECT_URI = "http://localhost:5000/callback"
SCOPE = "https://www.googleapis.com/auth/calendar"

# Used to store the token once captured
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
        f"&client_id={CLIENT_ID}"
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
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
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
    threading.Thread(target=run_flask_app, daemon=True).start()
    webbrowser.open("http://localhost:5000")

    # Wait until token is captured
    while "access_token" not in auth_token_data:
        pass  # You can use a better wait mechanism if needed

    return auth_token_data


# Calendar read function.
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
        return f"An error occurred: {error}"

def create_event(service, summary, description, start_time, end_time):
    """
    Add an event to the google calendar referenced by service

    Parameters:
    - service: Google calendar link
    - summary: Calendar event summary text
    - description: Calendar event description
    - start_time: Start date/time of Calendar event
    - end_time: End date/time of Calendar event
    """
    event_data = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/New_York',  # Adjust to your timezone
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'America/New_York',  # Adjust to your timezone
        },
    }
    new_event = service.events().insert(calendarId='primary', body=event_data).execute()
    print(f'Event created: {new_event.get("htmlLink")}')

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

    if not cal_events:
        print("No upcoming events found.")
        return None
    else:
        for event in cal_events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event.get('summary'))
        return cal_events


if __name__ == "__main__":
    """
    Get new events in an AirTable calendar and create Google Calendar events
    """
    # TBD: get calendar entries from airtable
    token_data = start_auth_flow()
    calendar_server = open_google_calendar(token_data.get("access_token"))
    if not calendar_server:
        # TBD: use airtable entries to create google calendar entries
        now = datetime.datetime.now()
        create_event(calendar_server, "This is a test", "testing creating a calendar event", now, now)
    else:
        print("ERROR: Calendar failed to open")
        exit(1)
