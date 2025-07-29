The folders below contain the sources for ATCalendar used by Wolf Pack to sync their 
AirTable events with Google Calendar events.

AuthMethod1 is my original version of ATCalendar that needed to be manually run and
used the authentication data of the current user.

AuthMethod2 is a modification of the original script to use the credentials json file
of a google service account, so the synchronization can be automated.

ATCalendar is a python script that can do one of the following:

- Imports AirTable calendar events into a Google Calendar.
- (Not Yet Tested)Deletes Google calendar entries based on deleted events information obtained from AirTable calendar events
- (Not Yet Tested)Updates Google calendar entries based on AirTable calendar events and data.

# Setup and Usage:

Use the following command to ensure the necessary python modules 
are installed locally:

  `python -m pip install flask gevent google google-api-python-client pyairtable`


usage: ATCalendar [-h] [-t TIME_STAMP]

Script to synchronize the Wolf PAC Google calendar with the AirTable calendar.

options:
  -h, --help            show this help message and exit
  -t, --time-stamp TIME_STAMP
                        Search for AirTable create/modify/delete events posted 
                        after TIME_STAMP