from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from tools.calendar_tools import list_events, create_event

def calendar_agent_node(state):
   
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
    tools = [list_events, create_event]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a calendar assistant. Manage schedule and events using the tools provided."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    
    result = executor.invoke({"input": state["messages"][-1].content, "chat_history": []})
    return {"messages": [result["output"]]}