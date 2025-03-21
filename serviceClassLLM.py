from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
import traceback

# Initialize the LLaMA 3.2 model
model = ChatOllama(model="llama3.2:latest", temperature=0)

# Setup conversation memory
memory = InMemoryChatMessageHistory(session_id="payment-session")

serviceDB = {'odisha':
        {
          'electricity':['OELE1', 'OELE2', 'OELE3'], 'gas':['OGAS1', 'OGAS2', 'OGAS3', 'OGAS4'], 'water':['OWAT1', 'OWAT2']
        },
    'goa':
        {
          'electricity':['GOELE1', 'GOELE2', 'GOELE2'], 'gas':['GOGAS1', 'GOGAS2', 'GOGAS3']
        },
    'telangana':
        {
          'electricity':['TSELE1', 'TSELE2', 'TSELE2', 'TSELE3'], 'gas':['TSGAS1', 'TSGAS2', 'TSGAS3']
        }
       }

# Define tool to fetch list of service providers
@tool
def fetch_service_provider(state: str, service: str)->str:
    """Fetches the list of providers based on user's state and bill service."""
    if state == '' or service == '':
        return f"Ask the user for the state and service."
    
    provList = serviceDB[state.lower()][service.lower()]
    print("HERE")

    return f"The service providers for {state} are: {provList}. Tell the entire list."

# Define tool to fetch bill details
@tool
def fetch_bill_details(state: str, provider: str, bill_number: str)->str:
    """Fetches bill details based on state, provider, and bill number."""
    # Simulated API response with static data for now
    return f"The bill amount for {provider} in {state} (Bill No: {bill_number}) is ₹145."

# Define tool to process payment
@tool
def process_payment(bill_number: str)->str:
    """Processes payment for the given bill number."""
    return f"Payment for Bill No: {bill_number} has been successfully processed."

tools = [fetch_bill_details, process_payment, fetch_service_provider]
# tools = [fetch_bill_details, process_payment]

# Define the conversational prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are PayLLM, a conversational payment assistant. NEVER call tools until you have collected all required information:\n"
               "You should never use external knowledge, assumptions or information beyond what is explicitly shared or recieved.\n"
               "Follow this strict sequence and do NOT proceed to the next step unless all information from the previous step is available:\n"
               "1. Greet the user if they greet you.\n"
               "2. Ask for the user their state and the service they want to pay the bill for.\n"
               "3. Get the list of service providers using fetch_service_provider tool.\n"
               "4. Ask for the service provider.\n"
               "5. Ask for the bill number.\n"
               "6. Confirm fetching the bill.\n"
               "7. Display the bill amount.\n"
               "8. Ask for payment confirmation.\n"
               "9. Confirm payment.\n"
               "Maintain the flow based on previous responses."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You name is AgentHi. You should always think about what to do, do not use any tool if it is not needed.\n"),
#     ("placeholder", "{chat_history}"),
#     ("human", "{input}"),
#     ("placeholder", "{agent_scratchpad}")
# ])



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
    # print(traceback.format_exc())
