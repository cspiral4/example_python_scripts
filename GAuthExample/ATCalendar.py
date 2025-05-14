#!python
#
# Make sure modules are installed first:
# python -m pip install flask gevent google google-api-python-client
#
# to run:
# python ATCalendar.py
#
import datetime

# AirTable utilities.
import AirTableUtils as ATUtils

# Google Calendar utilities.
import GoogleUtils as GUtils

# AirTable authentication info.
# replace your_airtable_pat, appXXXXXXXXXXXXXX, and tabld_id
# with the actual values
AT_PAT = "your_airtable_pat"
AT_BASE_ID = "appXXXXXXXXXXXXXX"
AT_TABLE_ID = "table_id"


if __name__ == "__main__":
    """
    Get new events in an AirTable calendar and create Google Calendar events
    """
    # Get AirTable calendar entries
    at_events = ATUtils.fetch_airtable_calendar(AT_PAT, AT_BASE_ID, AT_TABLE_ID, 50)
    if at_events is None:
        print("ERROR: Unable to open the AirTable Calendar")
        exit(1)

    # Open Google Calendar.
    # Get authentication token.
    token_data = GUtils.start_auth_flow()
    if token_data is None:
        print("ERROR: Unable to get Google authentication token")
        exit(1)
    # Open Calendar for read/write access.
    calendar_service = GUtils.open_google_calendar(token_data.get("access_token"))
    if calendar_service is None:
        print("ERROR: Google Calendar failed to open")
        exit(1)
    else:
        # Use airtable events to create google calendar events.
        for at_event in at_events:
            GUtils.create_event(calendar_service,
                                at_event["name"],
                                at_event["description"],
                                at_event["start_date"], at_event["end_date"])
