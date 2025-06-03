import requests
import datetime
from pyairtable import Api

def fetch_airtable_calendar(pat,
                            base_id,
                            table_id,
                            max_records=100,
                            time_filter=None
                            ):
    """
    Use pyAirtable module to get calendar entries from AirTable calendar.

    Parameters:
    - pat:  Personal Access Code to use for authentication.
    - base_id: base_id of airtable URL (appxxxxxxxxxxx).
    - table_id: id or name of the table to be read.
    - max_records: maximum number of record to download, default 100.
    - time_filter: compare creation timestamp to time_filter and only import
                   newer events only.

    Returns:
    - events: a list of the Calendar events to be imported to Google Calendar.
    """
    at_api = Api(pat)
    at_base = at_api.base(base_id)
    at_table = at_base.table(table_id)
    records = None

    if time_filter is None:
        # Get all records.  Should only do once.
        records = at_table.all()
    else:
        # Get all records created after time_filter.
        at_formula = f"CREATED_TIME() > '{time_filter}'"
        records = at_table.all(formula=at_formula)

    if records is None:
        print("INFO: No new events")
        return None

    events = []
    for record in records:
        fields = record.get("fields", {})
        event = {
            "summary": fields.get("Title"),
            "start": fields.get("Start Time"),
            "end": fields.get("End Time"),
            "description": fields.get("Description", ""),
            "recurrence": fields.get("Recurrence", "Once"),
            "location": fields.get("Location", ""),
            "attendees": fields.get("New Organizer Name"),
            "event_id": fields.get("Event ID"),
            "status": fields.get("Status")
        }
        events.append(event)

    return events

