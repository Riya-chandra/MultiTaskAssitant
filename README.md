# MultiTaskAssitant

MultiTaskAssitant: Autonomous Multi-Agent Personal Assistant

A Hierarchical Multi-Agent System that automates your daily workflow by integrating Gmail, Google Calendar, and Web Research into a single natural language interface.

📖 Overview

In today's digital workspace, we waste hours switching contexts between emails, calendars, and browser tabs. Intelli-Agent solves this by acting as a central command center.

Unlike standard chatbots that only generate text, this system takes real-world actions. It is built on a Hierarchical Multi-Agent Architecture where a "Supervisor Agent" intelligently delegates tasks to specialized "Worker Agents" (Email, Calendar, Research) to execute complex workflows autonomously.

✨ Key Features

🧠 Centralized Brain (Supervisor): Intelligently routes user queries to the correct department (Email vs. Calendar vs. Research) using LangGraph.

📧 Email Agent (Gmail): Reads unread emails, summarizes threads, and drafts/sends emails on your behalf.

📅 Calendar Agent (Google Calendar): Checks your schedule, finds free slots, and books new meetings automatically.

🔍 Research Agent (Tavily): Performs real-time web scraping and research (e.g., LinkedIn profiles, Tech News) to provide up-to-date answers.

💻 Dual Interface: * Terminal Mode: Fast, developer-centric CLI.

Streamlit UI: A polished, ChatGPT-like web interface.

💰 Cost-Optimized: Runs entirely on Google Gemini Pro (Free Tier), eliminating high OpenAI API costs.

🏗️ Architecture

The system follows a Supervisor-Worker Pattern:

graph TD
    User[User Request] --> Supervisor[Manager Agent]
    Supervisor -->|Routing| Email[Email Agent]
    Supervisor -->|Routing| Calendar[Calendar Agent]
    Supervisor -->|Routing| Research[Research Agent]
    
    Email --> GmailAPI[Gmail API]
    Calendar --> GCalAPI[Google Calendar API]
    Research --> Tavily[Tavily Search API]
    
    GmailAPI --> Response
    GCalAPI --> Response
    Tavily --> Response
    
    Response --> Supervisor
    Supervisor --> User


🛠️ Tech Stack

Core Framework: Python 3.10

Orchestration: LangGraph, LangChain

LLM: Google Gemini Pro (via langchain-google-genai)

Tools & APIs:

Google Gmail API

Google Calendar API

Tavily Search API

Frontend: Streamlit

Environment Management: Conda / Python-Dotenv

🚀 Installation & Setup

1. Clone the Repository

git clone [https://github.com/your-username/MultiTaskAssitant.git](https://github.com/Riya-chandra/MultiTaskAssitant.git)
cd ai-personal-assistant


2. Set up Environment

It is recommended to use Conda to avoid version conflicts.

conda create -n ai_assistant python=3.10 -y
conda activate ai_assistant
pip install -r requirements.txt


3. Configure Credentials

Create a .env file in the root directory:

# Get from Google AI Studio (Free)
GOOGLE_API_KEY=your_gemini_api_key_here

# Get from Tavily (Free)
TAVILY_API_KEY=your_tavily_api_key_here


4. Google Auth Setup

Download credentials.json from Google Cloud Console (Enable Gmail & Calendar APIs).

Place it in the root folder.

Run the auth script to generate token.json:

python setup_auth.py


💻 Usage

Option A: Web Interface (Recommended)

Launch the beautiful chat interface:

streamlit run ui.py


Option B: Terminal Mode

Run the assistant directly in your command line:

python app.py


🤖 Example Commands

Try asking your assistant these questions:

Calendar: "Do I have any meetings today?" or "Schedule a lunch meeting with Rahul tomorrow at 2 PM."

Email: "Check my unread emails and summarize them." or "Send an email to xyz@gmail.com saying I will be late."

Research: "Who is the CEO of OpenAI?" or "Search for the latest news on Python 3.13."

Complex: "Find the latest AI news and email the summary to my boss." (Requires multi-step reasoning).

🔮 Future Improvements

[ ] Notion Integration: Add a "Note-Taking Agent" to save research directly to Notion.

[ ] Slack Integration: Allow the assistant to read/reply to Slack messages.

[ ] Voice Mode: Add Speech-to-Text for voice commands.

👨‍💻 Author

Riya Chandra

Role: AI Engineer

Focus: Building Autonomous Agents & RAG Systems.

Note: This project is for educational purposes. Ensure you handle your credentials.json and token.json securely.

