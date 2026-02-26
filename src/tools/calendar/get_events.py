from datetime import datetime, timezone
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.utils import get_credentials
from dateutil import parser  # Add this import

class GetCalendarEventsInput(BaseModel):
    start_date: str = Field(description="Start date for fetching events in YYYY-MM-DD format or ISO format")
    end_date: str = Field(description="End date for fetching events in YYYY-MM-DD format or ISO format")

@tool("GetCalendarEvents", args_schema=GetCalendarEventsInput)
@traceable(run_type="tool", name="GetCalendarEvents")
def get_calendar_events(start_date: str, end_date: str):
    """Use this to get all calendar events between 2 time periods"""
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        # Flexible date parsing - handles multiple formats
        try:
            start_datetime = parser.parse(start_date)
        except:
            start_datetime = datetime.fromisoformat(start_date)
        
        try:
            end_datetime = parser.parse(end_date)
        except:
            end_datetime = datetime.fromisoformat(end_date)
        
        # Ensure UTC timezone
        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(tzinfo=timezone.utc)
        if end_datetime.tzinfo is None:
            end_datetime = end_datetime.replace(tzinfo=timezone.utc)
            
        # Set end time to end of day
        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)

        # Format date-times in RFC3339 format
        start_rfc3339 = start_datetime.isoformat().replace('+00:00', 'Z')
        end_rfc3339 = end_datetime.isoformat().replace('+00:00', 'Z')

        print(f"🔍 Fetching events from {start_rfc3339} to {end_rfc3339}")  # Debug

        events = service.events().list(
            calendarId='primary',
            timeMin=start_rfc3339,
            timeMax=end_rfc3339,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        if not events or 'items' not in events or len(events['items']) == 0:
            return "No events found in the specified time range."

        event_list = []
        for event in events['items']:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            description = event.get('description', 'No description')
            event_list.append(f"Event: {summary}, Description: {description}, Start: {start}")

        if event_list:
            result = "\n".join(event_list)
            print(f" Found {len(event_list)} events")  # Debug
            return result
        return "No events found for these dates"

    except HttpError as error:
        print(f" Calendar API error: {error}")
        return f"An error occurred: {error}"
    except Exception as e:
        print(f" Unexpected error: {e}")
        return f"Error fetching events: {str(e)}"