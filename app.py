import time
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from src.channels.telegram import TelegramChannel
from src.agents.personal_assistant import PersonalAssistant

# Load .env variables
load_dotenv()

# Initialize sqlite3 DB for saving agent memory
db_path = Path(__file__).resolve().parent / "db" / "checkpoints.sqlite"
db_path.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(db_path, check_same_thread=False)

# Use telegram for communicating with the agent
telegram = TelegramChannel()
# Use Slack for communicating with the agent
# slack = SlackChannel()

# Initiate personal assistant
personal_assistant = PersonalAssistant(conn)

# Configuration for the Langgraph checkpoints, specifying thread ID
config = {"configurable": {"thread_id": "1"}}


def monitor_channel(after_timestamp, config):
    while True:
        new_messages = telegram.receive_messages(after_timestamp)
        if new_messages:
            for message in new_messages:
                sent_message = (
                    f"Message: {message['text']}\n"
                    f"Current Date/time: {message['date']}"
                )
                answer = personal_assistant.invoke(sent_message, config=config)
                telegram.send_message(answer)
        after_timestamp = int(time.time())
        time.sleep(5)  # Sleep for 5 seconds before checking again
        

if __name__ == "__main__":
    print("Personal Assistant Manager is running")
    monitor_channel(int(time.time()), config)