from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def whatsapp_agent_node(state):
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    # Tum chaho toh yahan apna naam ya personality change kar sakte ho
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly and professional personal assistant. Answer general queries concisely."),
        ("human", "{input}"),
    ])
    
    chain = prompt | llm
    
    # User ka last message uthao
    last_message = state["messages"][-1].content
    
    # LLM se reply generate karo
    result = chain.invoke({"input": last_message})
    
    return {"messages": [result]}