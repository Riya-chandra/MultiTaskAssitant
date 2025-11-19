from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class RouterOutput(BaseModel):
    destination: str = Field(description="The agent to route to: 'email', 'calendar', 'research', or 'whatsapp'")

def manager_node(state):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_prompt = (
        "You are a supervisor. You must route the user request to one of the following workers:\n"
        "1. 'email': For reading or sending emails.\n"
        "2. 'calendar': For checking schedule or creating events.\n"
        "3. 'research': For searching info on web or LinkedIn.\n"
        "4. 'whatsapp': If the task is done or it's just a general greeting/reply.\n"
        "Output a JSON with a single key 'destination'."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | JsonOutputParser(pydantic_object=RouterOutput)
    
    last_message = state["messages"][-1]
    try:
        result = chain.invoke({"input": last_message.content})
        return {"next_agent": result["destination"]}
    except:
        return {"next_agent": "whatsapp"}