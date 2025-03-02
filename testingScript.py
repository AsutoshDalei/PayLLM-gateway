from langchain_core.tools import tool

from langchain_ollama import ChatOllama

model = ChatOllama(model="llama3.2", temperature=0)

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool

memory = InMemoryChatMessageHistory(session_id="test-session")
prompt = ChatPromptTemplate.from_messages(
    [
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
        # First put the history
        ("placeholder", "{chat_history}"),
        # Then the new input
        ("human", "{input}"),
        # Finally the scratchpad
        ("placeholder", "{agent_scratchpad}"),
    ]
)


@tool
def fetch_bill_details(state, provider, bill_number):
    """Fetches bill details based on state, provider, and bill number."""
    return f"The bill amount for {provider} in {state} (Bill No: {bill_number}) is ₹145."
@tool
def process_payment(bill_number):
    """Processes payment for the given bill number."""
    return f"Payment for Bill No: {bill_number} has been successfully processed."

tools = [fetch_bill_details, process_payment]


agent = create_tool_calling_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    # This is needed because in most real world scenarios, a session id is needed
    # It isn't really used here because we are using a simple in memory ChatMessageHistory
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

config = {"configurable": {"session_id": "test-session"}}

# print(agent_with_chat_history.invoke({"input": "Hi, I'm polly! What's the output of magic_function of 3?"}, config)["output"])
# print("---")
# print(agent_with_chat_history.invoke({"input": "Remember my name?"}, config)["output"])
# print("---")
# print(agent_with_chat_history.invoke({"input": "what was that output again?"}, config)["output"])

while True:
    userInput = input("User Input:\n -->")
    if userInput == '/end':
        break
    response = agent_with_chat_history.invoke({"input": userInput}, config)["output"]
    print(f"AI Response:\n--> {response}")
    print('---')