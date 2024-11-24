from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from websearch import execute_query

import openai
import os
os.environ["OPENAI_API_KEY"] = "" # add key here

# initialize tools for ReAct Agent
@tool
def summarize_query(query: str) -> str:
    """Summarizes a user query for search purposes."""
    prompt = PromptTemplate(
        input_variables=["query"],
        template="""
        You are a helpful assistant in charge of summarizing a web search based on information from a user. 
        
        Context:
        - If the user asks you to summarize a query, you should provide a concise summary of the query, it should be 
        suitable for a web search.

        Instructions:
        - Summarize the query in a few words to help with a web search.
        For example: If a person talks about properties in Singapore, search from the web and summarize the query.
        A sample query would be: Condominiums in Singapore. (use this as a template)

        Summarize this query for a web search: {query}
        """
    )
    summary_chain = LLMChain(llm=model, prompt=prompt)
    return summary_chain.run(query)

@tool
def simulate_web_search(user_query: str = "") -> str:
    """Simulated web search that returns dummy content based on the query."""
    # Here, we are simulating search results.
    # Replace this with `WebSearch.query()` for real search functionality.
    response = execute_query(user_query, num_results=8, content_length=5000)
    # return f"Simulated search results for '{query}':\n- Result 1: AI is advancing rapidly in 2023.\n- Result 2: New breakthroughs in AI for healthcare."
    response = "\n".join(response.values())
    return response

@tool
def summarize_content(content: str) -> str:
    """Summarizes web content into a concise summary."""
    prompt = PromptTemplate(
        input_variables=["content"],
        template="""
        You are an agent responsible to summarize web content for a user related to property listings.
        Once a user provides you with content, you should summarize it in a few sentences.

        Context:
        - Assume that a user gives you web content from a search result.
        - You need to idenify the important information about the property, you need to look at pricing 
        across different sites and come up with the price range, features about the property (number of rooms, kitchen, etc.)

        Instructions:
        - Given all the content, understand it carefully and summarize it such that it would be useful for a user
        from a property point of view.

        Summarize the following content as per instructions:\n{content}
        """
    )
    summarize_chain = LLMChain(llm=model, prompt=prompt)
    return summarize_chain.run(content)





# System Prompt
system_prompt = """
You are a helpful agent required to assist the user with their queries related to Real World Assets (RWAs) 
in Singapore specifically centered around property listings.

Imagine you've bought a house worth $5 million, putting down $1 million (20\% deposit) and financing the rest. 
Unfortunately, you lose your job and can't keep up with payments. Instead of risking foreclosure, you turn to Voxera for a solution.

Here's how it works:

	1.	Listing on platform: You list your house on our platform and set a timeframe by which you 
    plan to pay back the funds you raise. For example, you might commit to repurchasing the property within two years. 
    If you can't do this by the set time, the house will be sold, and the proceeds will go to the investors who bought shares.
	2.	Investment Options for Buyers: Voxera divides your property into small “shares” so investors can buy fractions of it:
	•	Conservative Investors can choose a low-risk approach, buying just 1\% of the house for $50,000.
	•	Riskier Investors can buy larger percentages if they're comfortable with more exposure.
	3.	Your Option to Buy Back: If your financial situation improves within the agreed timeframe, you can buy 
    back the house at market value, reclaiming full ownership. But if you're unable to, the property will be sold at 
    market rate, and the money will be distributed to all shareholders according to their ownership.

With our platform, investors get a low-barrier entry to real estate, and you, as the property owner, 
have a flexible option to overcome temporary financial difficulties, 
knowing exactly when you need to either repurchase or finalize the sale.

Instructions:
With all the information provided, you need to assist the user with their queries related to property listings.
"""

# initialize ReAct Agent
model = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [summarize_query, simulate_web_search, summarize_content]
agent_executor = create_react_agent(model, tools, state_modifier=system_prompt)

# User Query
user_query = {"messages": [("user", "What's the average rent in a unit at Marina Bay Residences, Singapore?")]}



# Get Response Stream
for s in agent_executor.stream(user_query, stream_mode="values"):
    message = s["messages"][-1]
    if isinstance(message, tuple):
        print(message)
    else:
        message.pretty_print()
