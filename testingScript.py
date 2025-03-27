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
You are PayLLM, an excellent and natural speaking virtual assistant for bill payments related tasks.

### General Rules:
- In the first user interaction, respond **directly** without calling any tools.
- Always **follow the structured step-by-step process** below.
- **Never assume information** or use external knowledge beyond what the user provides.
- **Ask only one question at a time** and store responses in memory before proceeding.
- DO NOT HALLUNICATE AND BE NATURAL IN YOUR RESPONSE.

### Step-by-Step Process:
0. Ask the user if they want to pay a bill.
1. Ask for their **state** in India.
2. Ask for their **service provider**.
3. Ask for their **bill number**.
4. Ask if they want to **fetch bill details**.
5. Fetch and inform them about the **bill amount**.
6. Ask if they want to **proceed with payment**.
7. If the user agrees, **pay the bill and confirm**.

Only fetch the bill details if all required information is collected.
"""


serviceDB = {
    'odisha': {
        'electricity': ['OELE1', 'OELE2', 'OELE3'],
        'gas': ['OGAS1', 'OGAS2', 'OGAS3', 'OGAS4'],
        'water': ['OWAT1', 'OWAT2']
    },
    'goa': {
        'electricity': ['GOELE1', 'GOELE2', 'GOELE3'],
        'gas': ['GOGAS1', 'GOGAS2', 'GOGAS3']
    },
    'telangana': {
        'electricity': ['TSELE1', 'TSELE2', 'TSELE3', 'TSELE4'],
        'gas': ['TSGAS1', 'TSGAS2', 'TSGAS3']
    },
    'maharashtra': {
        'electricity': ['MHELE1', 'MHELE2', 'MHELE3'],
        'gas': ['MHGAS1', 'MHGAS2', 'MHGAS3'],
        'water': ['MHWT1', 'MHWT2']
    },
    'kerala': {
        'electricity': ['KELE1', 'KELE2', 'KELE3'],
        'gas': ['KEGAS1', 'KEGAS2'],
        'water': ['KEWT1', 'KEWT2']
    },
    'karnataka': {
        'electricity': ['KAELE1', 'KAELE2', 'KAELE3'],
        'gas': ['KAGAS1', 'KAGAS2', 'KAGAS3'],
        'water': ['KAWT1', 'KAWT2']
    }
}


billDB = {
    "OGAS1": {"1234": "Rupees 145", "1357": "Rupees 512", "1245": "Rupees 918"},
    "OGAS2": {"1140": "Rupees 415", "1357": "Rupees 215", "1635": "Rupees 819"},
    "TSGAS2": {"2001": "Rupees 678", "2022": "Rupees 342", "2090": "Rupees 785"},
    "TSGAS3": {"3005": "Rupees 500", "3040": "Rupees 999", "3099": "Rupees 1200"},
    "TSELE2": {"4007": "Rupees 290", "4011": "Rupees 670", "4055": "Rupees 1020"},
    "TSELE3": {"5009": "Rupees 845", "5020": "Rupees 560", "5095": "Rupees 1325"}
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


# Tool to fetch bill details based on provider and bill number
@tool
def fetch_bill_details(provider: str, bill_number: str) -> str:
    """
    Fetches bill details based on provider and bill number.
    
    Args:
        provider (str): The name of the service provider.
        bill_number (str): The user's bill number.
        
    Returns:
        str: A message containing the bill amount or an appropriate error message.
    """
    # Check if both provider and bill number are provided
    if not provider or not bill_number:
        return "Please provide the service provider and bill number to fetch bill details."

    # Normalize input values
    provider = provider.strip().lower()
    bill_number = bill_number.strip()

    # Check if the provider exists in billDB
    if provider not in billDB:
        return f"Sorry, there are no records for provider '{provider}' in the billing database."

    # Check if the bill number exists in the provider's record in billDB
    if bill_number not in billDB[provider]:
        return f"Invalid bill number '{bill_number}' for provider '{provider}'. Please double-check your bill number."

    # Fetch and return the bill amount
    bill_amount = billDB[provider][bill_number]
    return f"The bill amount for '{provider}' (Bill No: {bill_number}) is {bill_amount}."

def event():
    memory = [SystemMessage(content = initialSystemMessage2), HumanMessage(content='Start my payment process.')]
    # memory = [SystemMessage(content = initialSystemMessage2)]

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

try:
    event()
except Exception as e:
    print(f"ERR: {e}")


