from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from tools.gmail_tools import read_emails, send_email

def email_agent_node(state):
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    tools = [read_emails, send_email]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an email assistant. Read and send emails using the tools provided."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    result = executor.invoke({"input": state["messages"][-1].content, "chat_history": []})
    return {"messages": [result["output"]]}