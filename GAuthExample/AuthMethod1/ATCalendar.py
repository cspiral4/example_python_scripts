#!python
#
# Make sure modules are installed first:
# python -m pip install flask gevent google google-api-python-client
#
# to run:
# python ATCalendar.py
#
import datetime
import argparse

# AirTable utilities.
import AirTableUtils as ATUtils

# Google Calendar utilities.
import GoogleUtils as GUtils

# AirTable authentication info.
# replace your_airtable_api_key, appXXXXXXXXXXXXXX, and Calendar
# with the actual values
AT_PAT = "your_airtable_api_key"
AT_BASE_ID = "appXXXXXXXXXXXXXX"
AT_TABLE_ID = "Calendar"


# CLI argument parsing.
def ParseArgs():
    at_parser = argparse.ArgumentParser(
                           prog='ATCalendar',
                           description='Script to synchronize the Wolf PAC Google calendar with the AirTable calendar.',
                          )

    at_parser.add_argument('-t', '--time-stamp', default="",
                           help='datetime string, in format yyyy-mm-ddThh:mm:ssZ, to use for event filtering'
                           )
    at_parser.add_argument('-d', '--delete', type=str,
                           help='Delete the Google calendar event whose Summary matches the delete value'
                           )
    at_parser.add_argument('-m', '--modify', type=str,
                           help='Modify the Google Calendar event whose Summary matches the modify value.  You must also specify the replacement source?'
                           )
    at_args = at_parser.parse_args()

    return at_args

if __name__ == "__main__":
    """
    Get new events in an AirTable calendar and create Google Calendar events
    """
    at_args = ParseArgs()
    at_events = None

    if not at_args.delete is None:
        # TBD: Delete the specified Google Calendar event.
        print("INFO: Event delete feature not yet implemented.")
        exit()

    if not at_args.modify is None:
        # TBD: find the matching Google entry and update it.
        print("INFO: Event modify feature not yet implemented.")
        exit()

    # Get new AirTable calendar entries
    if len(at_args.time_stamp) > 0:
        at_events = ATUtils.fetch_airtable_calendar(AT_PAT, AT_BASE_ID, AT_TABLE_ID, 50, at_args.time_stamp)
    else:
        at_events = ATUtils.fetch_airtable_calendar(AT_PAT, AT_BASE_ID, AT_TABLE_ID, 50)

    if at_events is None:
        print("ERROR: Unable to open the AirTable Calendar")
        exit(1)
    else:
        print("INFO: Downloaded %d events."%len(at_events))

    # Open Google Calendar.
    # Get authentication token.
    token_data = GUtils.start_auth_flow()
    if token_data is None:
        print("ERROR: Unable to get Google authentication token")
        exit(1)
    else:
        print("INFO: localhost service started")

    # Open Calendar for read/write access.
    calendar_service = GUtils.open_google_calendar(token_data.get("access_token"))
    if calendar_service is None:
        print("ERROR: Google Calendar failed to open")
        exit(1)
    else:
        print("INFO: Successfully opened google calendar")
        # Use airtable events to create google calendar events.
        for at_event in at_events:
            GUtils.create_event(calendar_service, at_event)
