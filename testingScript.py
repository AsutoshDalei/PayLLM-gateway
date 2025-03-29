# Importing necessary packages
import json

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Importing model
llm = ChatOllama(model="llama3.2:latest", temperature=0)

LANGUAGE = 'english'
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
- Respond back only in {}

### Follow the below Step-by-Step process:
0. Ask the user if they want to pay a bill.
1. Ask for their **state** in India and the utility service (electricity, water, gas).
2. Ask for their **consumer number**.
4. Fetch and inform them about the **consumer bill details**.
5. Ask if they want to **proceed with payment**.
6. If the user agrees, **pay the bill and confirm**.

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
    9182: {'Customer Name': 'John Doe', 'service provider': 'MHELE1', 'unit': 32, 'Amount': 341, 'Due Date': '10/01/2025', 'status': 'Paid', 'service': 'electricity'},
    1928: {'Customer Name': 'Jane Smith', 'service provider': 'MHELE2', 'unit': 37, 'Amount': 547, 'Due Date': '11/02/2025', 'status': 'Unpaid', 'service': 'electricity'},
    1038: {'Customer Name': 'David Brown', 'service provider': 'KEGAS1', 'unit': 23, 'Amount': 298, 'Due Date': '09/10/2025', 'status': 'Paid', 'service': 'electricity'},
    8321: {'Customer Name': 'Alice Johnson', 'service provider': 'OGAS1', 'Amount': 1008, 'Due Date': '04/03/2025', 'status': 'Paid', 'service': 'gas'},
    9120: {'Customer Name': 'Grace Lee', 'service provider': 'KEGAS1', 'Amount': 1024, 'Due Date': '06/22/2025', 'status': 'Unpaid', 'service': 'gas'},
    5310: {'Customer Name': 'Daniel Young', 'service provider': 'OGAS2', 'Amount': 1234, 'Due Date': '01/09/2025', 'status': 'Paid', 'service': 'gas'},
    8034: {'Customer Name': 'Lucas Perez', 'service provider': 'OWAT1', 'Amount': 935, 'Due Date': '02/03/2025', 'status': 'Unpaid', 'service': 'water'},
    2901: {'Customer Name': 'Zoe Mitchell', 'service provider': 'MHELE2', 'unit': 30, 'Amount': 520, 'Due Date': '04/10/2025', 'status': 'Paid', 'service': 'electricity'},
    5407: {'Customer Name': 'Ethan Lee', 'service provider': 'MHELE1', 'unit': 44, 'Amount': 700, 'Due Date': '08/16/2025', 'status': 'Unpaid', 'service': 'electricity'},
    1029: {'Customer Name': 'Chloe Adams', 'service provider': 'OGAS2', 'Amount': 960, 'Due Date': '01/12/2025', 'status': 'Paid', 'service': 'gas'},
    3410: {'Customer Name': 'Ryan Scott', 'service provider': 'KEGAS1', 'Amount': 1150, 'Due Date': '03/07/2025', 'status': 'Unpaid', 'service': 'gas'}
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


# Tool to fetch bill details based on consumer number
@tool
def fetch_bill_details(consumer_number: int) -> str:
    """
    Fetches bill details based on consumer number.
    Args:
        consumer_number (int): The user's consumer number.
        
    Returns:
        str: A message containing the bill amount or an appropriate error message.
    """
    # Check if both provider and bill number are provided
    if not consumer_number:
        return "Please provide the consumer number to fetch bill details."

    # Check if the bill number exists in the provider's record in billDB
    if consumer_number not in billDB:
        assert "BillNum Err"
        return f"Invalid consumer number '{consumer_number}'. Please double-check your bill number."

    # Fetch and return the bill amount
    bill_details = billDB[consumer_number]
    return f"The status of consumer number: {consumer_number} of {bill_details['service']} utility is {bill_details['status']} for rupees {bill_details['Amount']} due {bill_details['Due Date']}"
    

def event():

    LANGUAGE = input("Kindly mention the langauage you want to converse in (English, Hindi, Telugu):\n -->")

    memory = [SystemMessage(content = initialSystemMessage2.format(LANGUAGE)), HumanMessage(content='Start my payment process.')]
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
                    # print(f"TOOLCALL: {toolCall['name']}")
                    toolMsg = toolsMap[toolCall['name']].invoke(toolCall)
                    memory.append(toolMsg)
            aiMsg = llmTool.invoke(memory)
        print(f"AI Response:\n--> {aiMsg.content}\n")

try:
    event()
except Exception as e:
    print(f"ERR: {e}")

# script = ['Hello', "I live in Odisha", "I want to pay my gas bill", "My service provider is OGAS1 and my bill number is 123a4"]


