from datetime import datetime, timedelta
from dateutil import parser
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils import get_credentials

class AddEventToCalendarInput(BaseModel):
    title: str = Field(description="Title of the event")
    description: str = Field(description="Description of the event")
    start_time: str = Field(description="Start time of the event YYYY-MM-DD or ISO format")

@tool("AddEventToCalendar", args_schema=AddEventToCalendarInput)
@traceable(run_type="tool", name="AddEventToCalendar")
def add_event_to_calendar(title: str, description: str, start_time: str):
    "Use this to create a new event in my calendar"
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        event_title = title.strip()

        if "T" not in start_time:
            start_time = start_time + "T10:00:00"  # default 10 AM
        try:
            event_datetime = datetime.fromisoformat(start_time)
        except ValueError:
            event_datetime = parser.parse(start_time)

        end_datetime = event_datetime + timedelta(hours=1)
        existing_events = service.events().list(
            calendarId="primary",
            timeMin=event_datetime.isoformat() + "Z",
            timeMax=end_datetime.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute().get("items", [])

        for event in existing_events:
            if event.get("summary", "").lower() == event_title.lower():
                return f"⚠️ Event already exists: {event.get('htmlLink')}"
        event = {
            'summary': event_title,
            'description': description,
            'start': {
                'dateTime': event_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': (event_datetime + timedelta(hours=1)).isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
        }

        created = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created successfully. Title: {created.get('summary')}, Event ID: {created.get('id')}"

    except HttpError as error:
        return f"An error occurred: {error}"