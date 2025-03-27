# Importing necessary packages
import json

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Importing model
llm = ChatOllama(model="llama3.2:latest", temperature=0)

initialSystemMessage1 = '''You are PayLLM, a conversational payment assistant. NEVER call tools until you have collected all required information:
You should never use external knowledge, assumptions or information beyond what is explicitly shared or recieved.
Follow this strict sequence and do NOT proceed to the next step unless all information from the previous step is available:
1. Greet the user if they greet you.
2. Ask for the user their state and the service they want to pay the bill for.
3. Get the list of service providers using fetch_service_provider tool.
4. Ask for the service provider.
5. Ask for the bill number.
6. Confirm fetching the bill.
7. Display the bill amount.
8. Ask for payment confirmation.
9. Confirm payment.
Maintain the flow based on previous responses.

Ask these questions one at a time and remember it. Dont expect all at once. Fetch the bill only if you have all this information.
You should never use external knowledge, assumptions or information beyond what is explicitly shared or recieved. Refer to the example below.

Example:
User: Hello
PayLLM: Hi. To help with your payments, please provide your state.
User: Delhi.
PayLLM: Hi. Please provide your service provider.
User: Airtel.
PayLLM: Please provide your bill number.
User: 12345.
PayLLM: Sure, should I fetch the bill?
User: Yes, sure.
PayLLM: The bill amount is 145
User: Okay. Go ahead and pay it.
PayLLM: Sure.
PayLLM: The bill is paid.
'''

initialSystemMessage2 = """
You are PayLLM, an excellent virtual assistant for bill payments.

### General Rules:
- In the first user interaction, respond **directly** without calling any tools.
- Always **follow the structured step-by-step process** below.
- **Never assume information** or use external knowledge beyond what the user provides.
- **Ask only one question at a time** and store responses in memory before proceeding.

### Step-by-Step Process:
0. Ask the user if they want to pay a bill.
1. Ask for their **state**.
2. Ask for their **service provider**.
3. Ask for their **bill number**.
4. Ask if they want to **fetch bill details**.
5. Fetch and inform them about the **bill amount**.
6. Ask if they want to **proceed with payment**.
7. If the user agrees, **pay the bill and confirm**.

Only **fetch the bill details if all required information is collected.**

### Example Conversation:
User: Hello  
PayLLM: Hi! Do you want to pay a bill today?  

User: Yes.  
PayLLM: Great! Which state are you in?  

User: Delhi.  
PayLLM: Got it. Please provide your service provider.  

User: Airtel.  
PayLLM: Thanks. What is your bill number?  

User: 12345.  
PayLLM: Should I fetch the bill details for you?  

User: Yes, sure.  
PayLLM: The bill amount is ₹145.  

User: Okay. Go ahead and pay it.  
PayLLM: Sure! The bill has been successfully paid.
"""


serviceDB = {'odisha':
        {'electricity':['OELE1', 'OELE2', 'OELE3'], 'gas':['OGAS1', 'OGAS2', 'OGAS3', 'OGAS4'], 'water':['OWAT1', 'OWAT2']},
    'goa':{'electricity':['GOELE1', 'GOELE2', 'GOELE2'], 'gas':['GOGAS1', 'GOGAS2', 'GOGAS3']},
    'telangana':{'electricity':['TSELE1', 'TSELE2', 'TSELE2', 'TSELE3'], 'gas':['TSGAS1', 'TSGAS2', 'TSGAS3']}
    }

billDB = {
        "odisha": {"OGAS1": {"12345": "Rupees 145"}},
        "telangana": {"TSELE2": {"67890": "Rupees 200"}}
        }


@tool
def fetch_service_provider(state: str, service: str) -> str:
    """
    Fetches a list of service providers based on the user's state and bill service.
    Args:
        state (str): The state of residence of the user.
        service (str): The type of service for which the user wants to pay the bill.
    Returns:
        str: A message containing the list of service providers for the state, or an appropriate response if data is missing.
    """
    
    if not state or not service:
        return "Please specify both the state and the service type to fetch providers."
    
    state = state.strip().lower()
    service = service.strip().lower()

    if state not in serviceDB:
        return f"Sorry, I couldn't find service providers for '{state}'. Please check the state name."

    if service not in serviceDB[state]:
        return f"Sorry, there are no listed providers for '{service}' in '{state}'."

    # Fetch providers
    providers = serviceDB[state][service]

    return f"The available service providers for '{service}' in '{state}' are: {', '.join(providers)}."


@tool
def fetch_bill_details(state: str, provider: str, bill_number: str) -> str:
    """
    Fetches bill details based on state, provider, and bill number.
    Args:
        state (str): The state where the service provider operates.
        provider (str): The name of the service provider.
        bill_number (str): The user's bill number.
    Returns:
        str: A message containing the bill amount or an appropriate error message.
    """

    if not state or not provider or not bill_number:
        return "Please provide the state, service provider, and bill number to fetch bill details."

    state = state.strip().lower()
    provider = provider.strip().lower()
    bill_number = bill_number.strip()

    if state not in billDB:
        return f"Sorry, I couldn't find billing information for '{state}'. Please check the state name."
    
    if provider not in billDB[state]:
        return f"Sorry, there are no bill records for provider '{provider}' in '{state}'."

    if bill_number not in billDB[state][provider]:
        return f"Invalid bill number '{bill_number}' for '{provider}' in '{state}'. Please double-check your bill number."

    # Fetch and return bill details
    bill_amount = billDB[state][provider][bill_number]
    return f"The bill amount for '{provider}' in '{state}' (Bill No: {bill_number}) is {bill_amount}."

def event():
    memory = [SystemMessage(content = initialSystemMessage2), HumanMessage(content='Start my payment process.')]

    tools = [fetch_service_provider, fetch_bill_details]
    toolsMap = {"fetch_service_provider":fetch_service_provider, "fetch_bill_details":fetch_bill_details}


    llmService = llm
    llmTool = llm.bind_tools(tools)

    firstInteraction = True

    while True:
        userInput = input("User Input:\n -->").lower()
        if userInput == '/end':
            break
        memory.append(HumanMessage(content=userInput))
        aiMsg = llmTool.invoke(memory)

        if aiMsg.tool_calls:
            for toolCall in aiMsg.tool_calls:
                if toolCall['name'] in toolsMap:
                    toolMsg = toolsMap[toolCall['name']].invoke(toolCall)
                    memory.append(toolMsg)
            aiMsg = llmTool.invoke(memory)
        print(f"AI Response:\n--> {aiMsg.content}")



