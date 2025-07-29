#!python
import requests
import datetime
from pyairtable import Api
import datetime
import dateutil


# For monthly recurring events, determine the
# day of the week for the recurrences
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


# Construct a Monthly recurrence rule from AirTable data.
def construct_monthly_recurrence(event_data):
    """
    Using the start time, get the day of the week
    and week of the month, and construct a monthly
    recurrence rule on a specific day of the week.

    Parameters:
        at_event_data: AirTable calendar event data

    Returns:
        recurrence_rule: string containing a Google monthly recurrence rule.
    """
    recurrence_rule = ''

    # get start date.
    start_date = event_data.get('Start Time')
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

# Construct list of airtable calendar events to synch with
# Google Calendar and WordPress Events Calendar.
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
    rrules = None

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
        event_id = record.get('id')
        fields = record.get("fields", {})
        # FREQ rule for the calendar event needs extra
        # work if recurrence is monthly.
        # Repeat on first dayX of each month.
        # The rule syntax is common to both Google and WordPress.
        recur = fields.get('recurrence')
        if not recur == 'MONTHLY':
            # rule that works for ONCE and WEEKLY
            rrules = f'RRULE:FREQ={recur}'
        else:
            rrules = construct_monthly_recurrence(fields)
        event = {
            "summary": fields.get("Title"),
            "start": fields.get("Start Time"),
            "end": fields.get("End Time"),
            "description": fields.get("Description", ""),
            "recurrence": rrules,
            "location": fields.get("Location", ""),
            "attendees": fields.get("New Organizer Name"),
            "event_id": event_id,
            "request_type": fields.get("Request Type")
        }
        events.append(event)

    return events

def delete_event(pat,
                 base_id,
                 table_id,
                 event_id):
    at_api = Api(pat)
    at_base = at_api.base(base_id)
    at_table = at_base.table(table_id)
    response = at_table.delete(event_id)

    if response and response.get('deleted'):
        print("INFO: AirTable calendar event with event id %s deleted"%event_id)
    else:
        print("ERROR: Failed to deleted AirTable calendar event with event id %s: %s"
              %(event_id,response))

    return response
