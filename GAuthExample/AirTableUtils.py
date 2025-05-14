import requests
import datetime
from pyairtable import Api

def fetch_airtable_calendar(pat, base_id, table_id, max_records=100):
    """
    Use pyAirtable module to get calendar entries from AirTable calendar.

    Parameters:
    - pat:  Personal Access Code to use for authentication.
    - base_id: base_id of airtable URL (appxxxxxxxxxxx).
    - table_id: id or name of the table to be read.
    - max_records: maximum number of record to download, default 100.

    Returns:
    - events: a list of the Calendar events to be imported to Google Calendar.
    """
    at_api = Api(pat)
    at_base = at_api.base(base_id)
    at_table = at_base.table(table_id)
    records = at_table.all()

    events = []
    for record in records:
        fields = record.get("fields", {})

        event = {
            "name": fields.get("Title"),
            "start_date": fields.get("Start Time"),
            "end_date": fields.get("End Time"),
            "description": fields.get("Description", "")
        }

        # Parse the dateS into a datetime object.
        if event["start_date"]:
            try:
                event["start_date"] = datetime.datetime.fromisoformat(event["start_date"].replace('Z', '+00:00'))
            except ValueError:
                print("WARNING: Unable to convert start_date to datetime format for %s"%event["name"])
        if event["end_date"]:
            try:
                event["end_date"] = datetime.datetime.fromisoformat(event["end_date"].replace('Z', '+00:00'))
            except ValueError:
                print("WARNING: Unable to convert end_date to datetime format for %s"%event["name"])

        events.append(event)

    return events

