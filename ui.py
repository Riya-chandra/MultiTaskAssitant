# import streamlit as st
# import operator
# from typing import TypedDict, Annotated, List
# from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
# from langgraph.graph import StateGraph, END
# from dotenv import load_dotenv

# # --- Import Agents (Tumhare Banaye Hue) ---
# from agents.manager_agent import manager_node
# from agents.email_agent import email_agent_node
# from agents.calendar_agent import calendar_agent_node
# from agents.research_agent import research_agent_node

# # Load Environment
# load_dotenv()

# # --- 1. Setup Graph (Brain) ---
# class AgentState(TypedDict):
#     messages: Annotated[List[BaseMessage], operator.add]
#     next_agent: str

# workflow = StateGraph(AgentState)

# workflow.add_node("manager", manager_node)
# workflow.add_node("email", email_agent_node)
# workflow.add_node("calendar", calendar_agent_node)
# workflow.add_node("research", research_agent_node)

# workflow.set_entry_point("manager")

# def route_agent(state):
#     return state["next_agent"]

# workflow.add_conditional_edges(
#     "manager",
#     route_agent,
#     {
#         "email": "email",
#         "calendar": "calendar",
#         "research": "research"
#     }
# )

# workflow.add_edge("email", END)
# workflow.add_edge("calendar", END)
# workflow.add_edge("research", END)

# app_graph = workflow.compile()

# # --- 2. Streamlit UI Code ---

# st.set_page_config(page_title="My AI Assistant", page_icon="🤖")

# st.title("🤖 Multi Task AI Assistant")
# st.caption("Managed by: Gemini Pro | Tools: Google Calendar, Gmail, Web Search")

# # Session State (Chat History Save karne ke liye)
# if "messages" not in st.session_state:
#     st.session_state["messages"] = [
#         {"role": "assistant", "content": "Hello! I m your personal Assitant Riya Chandra mam.... Mai Email, Calendar aur Research handle kar sakta hu. Boliye kya karu?"}
#     ]

# # Purane messages dikhao
# for msg in st.session_state.messages:
#     st.chat_message(msg["role"]).write(msg["content"])

# # User Input Box
# user_input = st.chat_input("enter your Query.... (e.g., Check my meetings today)")

# if user_input:
  
#     st.session_state.messages.append({"role": "user", "content": user_input})
#     st.chat_message("user").write(user_input)

   
#     with st.spinner("I m thinking wait mam... 🧠"):
#         try:
          
#             inputs = {
#                 "messages": [HumanMessage(content=user_input)],
#                 "next_agent": ""
#             }
            
#             final_response = "Sorry i can't get it Riya mam."
            
           
#             for event in app_graph.stream(inputs):
#                 for key, value in event.items():
#                     if "messages" in value:
#                         last_msg = value["messages"][-1]
#                         if key != "manager": 
#                             final_response = last_msg.content
            
           
#             st.session_state.messages.append({"role": "assistant", "content": final_response})
#             st.chat_message("assistant").write(final_response)
            
#         except Exception as e:
#             st.error(f"Error: {e}")