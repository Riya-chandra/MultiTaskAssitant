import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

@tool
def web_search(query: str):
    """Perform a web search using Tavily to find general information on the internet."""
    tool = TavilySearchResults(max_results=5)
    results = tool.invoke({"query": query})
    return results

@tool
def linkedin_research(name: str, company: str = ""):
    """Search for a specific person's LinkedIn profile and professional details."""
    search_query = f"site:linkedin.com {name} {company} profile info"
    tool = TavilySearchResults(max_results=3)
    results = tool.invoke({"query": search_query})
    return results