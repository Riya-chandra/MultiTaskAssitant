import os
import uvicorn
from fastapi import FastAPI, Form, Response
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator
from langchain_core.messages import HumanMessage  # <--- Ye line add karo top par
from pyngrok import ngrok  # <-- Ye zaroori hai auto-connect ke liye

# Import Agents
from agents.manager_agent import manager_node
from agents.email_agent import email_agent_node
from agents.calendar_agent import calendar_agent_node
from agents.research_agent import research_agent_node
from agents.whatsapp_agent import whatsapp_agent_node # <-- Ye missing tha

from tools.whatsapp_sender import send_whatsapp_message

# Load Environment
from dotenv import load_dotenv
load_dotenv()

# --- 1. Define State ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_agent: str

# --- 2. Build Graph ---
workflow = StateGraph(AgentState)

# Add Nodes (Agents)
workflow.add_node("manager", manager_node)
workflow.add_node("email", email_agent_node)
workflow.add_node("calendar", calendar_agent_node)
workflow.add_node("research", research_agent_node)
workflow.add_node("whatsapp", whatsapp_agent_node) # <-- Ye naya node hai

# Add Edges (Logic)
workflow.set_entry_point("manager")

# Conditional Logic: Manager -> Specific Agent
def route_agent(state):
    return state["next_agent"]

workflow.add_conditional_edges(
    "manager",
    route_agent,
    {
        "email": "email",
        "calendar": "calendar",
        "research": "research",
        "whatsapp": "whatsapp" # <-- Ab ye whatsapp agent ke paas jayega
    }
)

# Return Logic: Agent -> Manager (Loop)
workflow.add_edge("email", "manager")
workflow.add_edge("calendar", "manager")
workflow.add_edge("research", "manager")
workflow.add_edge("whatsapp", END) # <-- Baat khatam hone par ruk jayega

app_graph = workflow.compile()

# --- 3. WhatsApp Server (FastAPI) ---
app = FastAPI()

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...), To: str = Form(...)):
    print(f"📩 Message from {From}: {Body}")
    

    inputs = {
        "messages": [HumanMessage(content=Body)],
        "next_agent": ""  # Initial state mein empty string
    }
    
    output = app_graph.invoke(inputs)
    
    # Last message nikalo
    final_response = output["messages"][-1].content
    
    print(f"📤 Sending reply to {From} via {To}")
    send_whatsapp_message.invoke({
        "to_number": From, 
        "body": final_response,
        "from_number": To
    })
    
    return Response(content="OK", media_type="text/plain")

if __name__ == "__main__":
    
    NGROK_AUTH_TOKEN = "35gyrfBDCoYQ6bpNm48TYYnqTuH_5ApBv5A1Wtjt95tcQwNu8" 

    
    # Ngrok Connect
    try:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        public_url = ngrok.connect(5000).public_url
        print("="*60)
        print(f"🚀 PUBLIC URL: {public_url}")
        print(f"👉 Copy this URL and paste into Twilio Sandbox: {public_url}/whatsapp")
        print("="*60)
    except Exception as e:
        print(f"⚠️ Ngrok Error: {e}")
        print("Continuing without auto-ngrok...")

    print("🚀 AI Assistant is Running on Port 5000...")
    uvicorn.run(app, host="0.0.0.0", port=5000)