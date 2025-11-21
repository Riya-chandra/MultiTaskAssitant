# from langgraph.checkpoint.sqlite import SqliteSaver
from src.agents.base import Agent, AgentsOrchestrator
from src.prompts import *
from src.tools.calendar import *
from src.tools.email import *
from src.tools.research import *
from src.utils import get_current_date_time

class PersonalAssistant:
    def __init__(self, db_connection):
        # Create sqlite checkpointer for managing manager memory
        self.checkpointer =db_connection
        
        # Initialize individual agents
        self.email_agent = Agent(
            name="email_agent",
            description="Email agent can manage GMAIL inbox including read and send emails",
            model="groq/llama-3.3-70b-versatile",
            system_prompt=EMAIL_AGENT_PROMPT.format(date_time=get_current_date_time()),
            tools=[read_emails, send_email, find_contact_email],
            sub_agents=[],
            temperature=0.1,
            memory=None 
        )

        self.calendar_agent = Agent(
            name="calendar_agent",
            description="Calendar agent can manage Google Calendar including get events and create events",
            model="groq/llama-3.3-70b-versatile",
            system_prompt=CALENDAR_AGENT_PROMPT.format(date_time=get_current_date_time()),
            tools=[get_calendar_events, add_event_to_calendar, find_contact_email],
            sub_agents=[],
            temperature=0.1
        )

        self.researcher_agent = Agent(
            name="researcher_agent",
            description="Researcher agent can search the web, scrape websites or LinkedIn profiles",
            model="groq/llama-3.3-70b-versatile",
            system_prompt=RESEARCHER_AGENT_PROMPT.format(date_time=get_current_date_time()),
            tools=[search_web, scrape_website_to_markdown, search_linkedin_tool],
            sub_agents=[],
            temperature=0.1
        )

        # Initialize the manager agent
        self.manager_agent = Agent(
                    name="manager_agent",
                    description="Manager agent",
                    model="groq/llama-3.3-70b-versatile",
                    system_prompt=ASSISTANT_MANAGER_PROMPT.format(date_time=get_current_date_time()),
                    tools=[],
                    sub_agents=[
                        self.email_agent,
                        self.calendar_agent,
                        self.researcher_agent
                    ],
                    temperature=0.1,
                    memory=self.checkpointer  
                )
 
        # Initialize the orchestrator
        self.assistant_orchestrator = AgentsOrchestrator(
            main_agent=self.manager_agent,
            agents=[
                self.manager_agent,
                self.email_agent,
                self.calendar_agent,
                self.researcher_agent
            ]
        )

    def __getattr__(self, name):
        return getattr(self.assistant_orchestrator, name)
