# Importing necessary packages
import json

from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# memory = InMemoryChatMessageHistory(session_id="test-session")

llm = ChatOllama(model="llama3.2", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are PayLLM, a conversational payment assistant. "
               "Follow this structured flow:\n"
               "1. Ask the user for their state.\n"
               "2. Ask for the service provider.\n"
               "3. Ask for the bill number.\n"
               "4. Confirm fetching the bill.\n"
               "5. Display the bill amount.\n"
               "6. Ask for payment confirmation.\n"
               "7. Confirm payment.\n"
               "Maintain the flow based on previous responses."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

@tool
def fetch_bill_details(state, provider, bill_number):
    """Fetches bill details based on state, provider, and bill number."""
    return f"The bill amount for {provider} in {state} (Bill No: {bill_number}) is ₹145."
@tool
def process_payment(bill_number):
    """Processes payment for the given bill number."""
    return f"Payment for Bill No: {bill_number} has been successfully processed."

tools = [fetch_bill_details, process_payment]
agent = create_react_agent(llm, tools, prompt=prompt)

# query = 'Hello'
# print(agent_executor.invoke({"input": query}))

# agent = create_react_agent(llm, tools, prompt)


while True:
    userInput = input("User Input:\n -->")
    if userInput == '/end':
        break
    # response = agent.invoke({"input": userInput, "chat_history": memory.chat_memory.messages})
    response = agent.invoke({"input": userInput})
    # memory.save_context({"input": userInput}, {"output": response})
    print(f"AI Response:\n--> {response}")