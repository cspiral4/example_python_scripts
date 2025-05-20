ATCalendar is a python script that can do one of the following:

- Imports Wolf PAC AirTable calendar events into the Wolf PAC Google Calendar.
- (Not Yet Implemented)Deletes Google calendar entries based on deleted events information obtained from Wolf PAC AirTable calendar data
- (Not Yet Implemented)Updates Google calendar entries based on Wolf PAC AirTable calendar data.

# Setup and Usage:

Use the following command to ensure the necessary python modules 
are installed locally:

  `python -m pip install flask gevent google google-api-python-client pyairtable`


usage: ATCalendar [-h] [-t TIME_STAMP] [-d DELETE] [-m MODIFY]

Script to synchronize the Wolf PAC Google calendar with the AirTable calendar.

options:
  -h, --help            show this help message and exit
  -t, --time-stamp TIME_STAMP
                        datetime string, in format yyyy-mm-ddThh:mm:ssZ,
                        to use for event filtering.  Retrieves events
                        created after the TIME_STAMP
  -d, --delete DELETE   Delete the Google calendar event whose Summary
                        matches the delete value
  -m, --modify MODIFY   Modify the Google Calendar event whose Summary
                        matches the modify value. You must also specify
                        the replacement source?