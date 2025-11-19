import os
from twilio.rest import Client
from langchain_core.tools import tool

@tool
def send_whatsapp_message(to_number: str, body: str, from_number: str = None):
    """Send a WhatsApp message to a user."""
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    if from_number is None:
        from_number = os.environ.get('TWILIO_FROM_NUMBER', 'whatsapp:+14155238886')

    message = client.messages.create(
        from_=from_number,
        body=body,
        to=to_number
    )
    return f"Message sent! SID: {message.sid}"