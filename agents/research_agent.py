from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
# Hum tools folder se import kar rahe hain
from tools.linkedin_scraper import web_search, linkedin_research

def research_agent_node(state):
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    tools = [web_search, linkedin_research]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a research assistant. Use web search and LinkedIn tools to find information."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    
    # State se last message nikal kar process karte hain
    result = executor.invoke({"input": state["messages"][-1].content, "chat_history": []})
    
    return {"messages": [result["output"]]}