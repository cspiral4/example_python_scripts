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
AT_BASE_ID = "appXXXXXXXXXXXX"
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
    at_args = at_parser.parse_args()

    return at_args

if __name__ == "__main__":
    """
    Get events in an AirTable calendar and create, modify, or delete
    Google Calendar events.
    """
    at_args = ParseArgs()
    at_events = None

    # Get new AirTable calendar entries
    if len(at_args.time_stamp) > 0:
        at_events = ATUtils.fetch_airtable_calendar(
            AT_PAT,
            AT_BASE_ID,
            AT_TABLE_ID, 50,
            at_args.time_stamp)
    else:
        at_events = ATUtils.fetch_airtable_calendar(
            AT_PAT,
            AT_BASE_ID,
            AT_TABLE_ID, 50)

    if at_events is None:
        print("ERROR: Unable to open the AirTable Calendar")
        exit(1)
    else:
        print("INFO: Downloaded %d events."%len(at_events))

    # Open Calendar for read/write access.
    google_service = GUtils.open_google_calendar()
    if google_service is None:
        print("ERROR: Google Calendar failed to open")
        exit(1)
    print("INFO: Successfully opened google calendar")

    # Use airtable events to create or modify google calendar events.
    for at_event in at_events:
        request_type = at_event['request_type']
        summary = at_event['summary']
        if request_type == 'New Event':
            print("DEBUG: Creating a new event")
            GUtils.create_event(google_service, at_event)
        elif request_type == 'Change Event':
            print("DEBUG: Modifying an event")
            GUtils.modify_event(google_service, at_event)
        elif request_type == 'Delete Event':
            print("DEBUG: Deleting an event")
            GUtils.delete_event(google_service, at_event['event_id'])
        else:
            print("ERROR: Unrecognized AirTable calendar request type %s, ignoring: %s"
                  %(request_type, summary))

    print("INFO: Updates complete.  Be sure to check the output for errors")
