from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory

# Initialize the LLaMA 3.2 model
model = ChatOllama(model="llama3.2", temperature=0)

# Setup conversation memory
memory = InMemoryChatMessageHistory(session_id="payment-session")

# Define tool to fetch bill details
@tool
def fetch_bill_details(state: str, provider: str, bill_number: str):
    """Fetches bill details based on state, provider, and bill number."""
    # Simulated API response with static data for now
    return f"The bill amount for {provider} in {state} (Bill No: {bill_number}) is ₹145."

# Define tool to process payment
@tool
def process_payment(bill_number: str):
    """Processes payment for the given bill number."""
    return f"Payment for Bill No: {bill_number} has been successfully processed."

tools = [fetch_bill_details, process_payment]

# Define the conversational prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are PayLLM, a conversational payment assistant. "
               "Follow this structured flow:\n"
               "1. Greet the user if they greet you.\n"
               "2. Ask for the user's state.\n"
               "3. Ask for the service provider.\n"
               "4. Ask for the bill number.\n"
               "5. Confirm fetching the bill.\n"
               "6. Display the bill amount.\n"
               "7. Ask for payment confirmation.\n"
               "8. Confirm payment.\n"
               "Maintain the flow based on previous responses."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create the agent for handling tool calls
agent = create_tool_calling_agent(model, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Wrap with memory to manage the conversation history
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Configuration for session tracking
config = {"configurable": {"session_id": "payment-session"}}


# Chat loop to interact with the user
try:
    while True:
        user_input = input("User Input:\n --> ")
        if user_input.lower() == '/end':  # End the conversation if the user types '/end'
            break
        # Invoke the agent to handle the conversation and return the response
        response = agent_with_chat_history.invoke({"input": user_input}, config)["output"]
        
        # Print the agent's response
        print(f"AI Response:\n--> {response}")
        print('---')
except Exception as e:
    print("ERR", e)
