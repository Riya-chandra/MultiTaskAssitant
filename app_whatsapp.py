import uvicorn
import asyncio
from fastapi import FastAPI, Form
from dotenv import load_dotenv
from src.channels.whatsapp import WhatsAppChannel
from src.agents.personal_assistant import PersonalAssistant
from src.utils import get_current_date_time

load_dotenv()
app = FastAPI()

personal_assistant = PersonalAssistant(None)

async def process_message_async(to_whatsapp_number, incoming_message):
    try:
        print(f"\n--- Processing message for {to_whatsapp_number} ---\n")
        
        message = (
            f"Message: {incoming_message}\n"
            f"Current Date/time: {get_current_date_time()}"
        )
        
        print("Invoking assistant...")
        answer = personal_assistant.invoke(message)
        # answer = f"I received your command RIYA: {incoming_message}"
        
        print(f"Got response: {answer[:100]}...")
        
        print("Sending WhatsApp message...")
        whatsapp = WhatsAppChannel()
        result = await asyncio.to_thread(
            whatsapp.send_message,
            to_number=to_whatsapp_number,
            body=answer
        )
        print(f"WhatsApp send result: {result}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    print(f"Message received from {From}: {Body}")
    asyncio.create_task(process_message_async(From, Body))
    return "Message received", 200

if __name__ == "__main__":
    print("WhatsApp Personal Assistant server is running...")
    uvicorn.run(app, host="0.0.0.0", port=5000)