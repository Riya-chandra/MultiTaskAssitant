from langchain_google_genai import ChatGoogleGenerativeAI  # <--- Ye zaroori hai
from langchain_core.prompts import ChatPromptTemplate

def whatsapp_agent_node(state):

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly and professional personal assistant. Answer general queries concisely."),
        ("human", "{input}"),
    ])
    
    chain = prompt | llm
    
    last_message = state["messages"][-1].content
    
    result = chain.invoke({"input": last_message})
    
    return {"messages": [result]}