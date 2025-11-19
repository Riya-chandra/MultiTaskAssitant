import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from langchain_core.tools import tool

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        return None
    return build('calendar', 'v3', credentials=creds)

@tool
def list_events():
    """Retrieve the next 5 upcoming events from the calendar."""
    service = get_calendar_service()
    if not service:
        return "Authentication failed."
    
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=5, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return "No upcoming events found."

    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_list.append(f"Time: {start}, Event: {event['summary']}")
    
    return "\n".join(event_list)

@tool
def create_event(summary: str, start_time: str, end_time: str):
    """Create a new event in the calendar with a summary, start time, and end time."""
    service = get_calendar_service()
    if not service:
        return "Authentication failed."
        
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'},
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    return f"Event created: {event.get('htmlLink')}"
