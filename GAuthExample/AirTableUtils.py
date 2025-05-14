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
            "summary": fields.get("Title"),
            "start": fields.get("Start Time"),
            "end": fields.get("End Time"),
            "description": fields.get("Description", ""),
            "recurrence": fields.get("Recurrence", "Once")
        }
        events.append(event)

    return events

