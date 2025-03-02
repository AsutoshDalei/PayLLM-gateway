from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory

# Initialize LLaMA 3.2 Model
model = ChatOllama(model="llama3.2:latest", temperature=0)

# Memory setup
memory = InMemoryChatMessageHistory(session_id="test-session")

# Define tools
@tool
def fetch_bill_details(state: str, provider: str, bill_number: str):
    """Fetches bill details based on state, provider, and bill number."""
    return f"The bill amount for {provider} in {state} (Bill No: {bill_number}) is ₹145."

@tool
def process_payment(bill_number: str):
    """Processes payment for the given bill number."""
    return f"Payment for Bill No: {bill_number} has been successfully processed."

tools = [fetch_bill_details, process_payment]

# Define prompt to ensure proper flow
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are PayLLM, a conversational payment assistant."
               "Follow this structured flow:\n"
               "1. Greet the user if they greet you.\n"
               "2. Ask for their state.\n"
               "3. Ask for the service provider.\n"
               "4. Ask for the bill number.\n"
               "5. Confirm fetching the bill.\n"
               "6. Display the bill amount.\n"
               "7. Ask for payment confirmation.\n"
               "8. Confirm payment.\n"
               "Maintain the flow based on previous responses.\n"
               "The assistant should **never mention errors** or missing bill details in the flow. Just continue with the prompts until all necessary information is gathered."
               ),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create the agent
agent = create_tool_calling_agent(model, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)

# Wrap with history management
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# Configuration for session tracking
config = {"configurable": {"session_id": "test-session"}}


# Chat loop
try:
    while True:
        userInput = input("User Input:\n --> ")
        if userInput.lower() == '/end':
            break
        response = agent_with_chat_history.invoke({"input": userInput}, config)["output"]
        print(f"AI Response:\n--> {response}")
        print('---')
except Exception as e:
    print("ERR", e)
