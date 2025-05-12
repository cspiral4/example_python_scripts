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

# Replace with your actual values
CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"
REDIRECT_URI = "http://localhost:5000/callback"
SCOPE = "https://www.googleapis.com/auth/calendar"

# Used to store the token once captured
auth_token_data = {}

# Authentication functions, using Flask to create a web server process.

# index defines the default URI used when the server starts the Flask app.
@app.route("/")
def index():
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
# this step requires human interaction to confirm - may be due to google brand and
# other settings.
@app.route("/callback")
def callback():
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

# Starts a web server running the defined Flask app.
def run_flask_app():
    http_server = WSGIServer(('localhost',5000), app)
    http_server.serve_forever()

# Start the web server and wait for the authentication token.
def start_auth_flow():
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
    Reads events from the user's primary Google Calendar using an OAuth 2.0 token.

    Parameters:
    - access_token (str): A valid OAuth 2.0 access token for Google Calendar API.

    Returns:
    - List of upcoming events or error message.
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
  event = {
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
  event = service.events().insert(calendarId='primary', body=event).execute()
  print(f'Event created: {event.get("htmlLink")}')


if __name__ == "__main__":
    # TBD: get calendar entries from airtable
    token_data = start_auth_flow()
    calendar_server = open_google_calendar(token_data.get("access_token"))
    if calendar_server is not None:
        # TBD: use airtable entries to create google calendar entries
        now = datetime.datetime.now()
        create_event(calendar_server, "This is a test", "testing creating a calendar event", now, now)
    else:
        print("ERROR: Calendar failed to open")
