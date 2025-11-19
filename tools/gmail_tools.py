import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from langchain_core.tools import tool

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            return None
    return build('gmail', 'v1', credentials=creds)

@tool
def read_emails(query: str = "is:unread"):
    """Read emails from Gmail matching the query (default is unread)."""
    service = get_service()
    if not service:
        return "Authentication failed."
    
    results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
    messages = results.get('messages', [])
    
    email_data = []
    if not messages:
        return "No emails found."
        
    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = txt['payload']
        headers = payload.get("headers")
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")
        snippet = txt.get('snippet')
        email_data.append(f"From: {sender}, Subject: {subject}, Snippet: {snippet}")
        
    return "\n".join(email_data)

@tool
def send_email(to_email: str, subject: str, body: str):
    """Send an email to a specific recipient with a subject and body."""
    service = get_service()
    if not service:
        return "Authentication failed."
        
    message = EmailMessage()
    message.set_content(body)
    message['To'] = to_email
    message['From'] = 'me'
    message['Subject'] = subject
    
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    
    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        return f"Email sent! Id: {message['id']}"
    except Exception as error:
        return f"An error occurred: {error}"