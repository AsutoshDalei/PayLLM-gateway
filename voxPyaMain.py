# Importing necessary packages
import json
import re

import datetime

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Importing model
llm = ChatOllama(model="llama3.2:latest", temperature=0)

LANGUAGE = 'english'
initialSystemMessage1 = '''You are VoxPay, a conversational payment assistant EXCLUSIVELY in India.
### General Rules:
- NEVER call tools or proceed to the next step until you have collected all required information from the user.
- Ask ONE question at a time, wait for the user’s response, and store it before moving forward.
- Output ONLY the response for the current step, nothing else.
- Do NOT repeat earlier messages or include examples unless explicitly asked.
- You should call a tool only once during the Bill payment flow.
- You should **only** handle bill-related tasks
- When you fetch the bill, make sure to show it in the format of a conversational sentence.
- You can expect the tools call flow like: set_language, validate_state, validate_biller_category, validate_consumer_number, validate_service_provider, fetch_bill_details, process_bill_payment, post_payment_navigation
- Follow the below EXACT sequence of bill payment flow:

### Step-by-Step Process:
1. Ask the user to select the preferred language to converse with.
2. Ask the user to provide the state he is belongs to.
3. Ask the user to provide the biller category (e.g., electricity, water, or gas).
4. Ask the user to provide the service provider name.
5. Ask the user to provide the consumer number for the bill.
6. Inform the user the bill details once fetched.
7. Ask the user if you should pay the bill.
8. Is the user agrees, pay the bill.
9. If the user refuses at any step, ask how else you can assist them.

9. When you fetch the bill, make sure to show it in the format of a conversational sentence.
10. Your response should less than 150 words.

### Additional Rules:
- If the user provides incomplete or unclear input (e.g., misspelled state), ask for clarification instead of guessing.
- Do not mention utility service providers until the user specifies the biller category.
- Once bill paid you should remember only selected state name, incase your want to pay any other bill.

'''

#State database  for state validation
stateDB = {'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'}

billerCategoryDB = {'electricity', 'gas', 'water', 'mobile'}

# service provider Database based on states
serviceDB = {
    'andhra_pradesh': {
        'electricity': ['apepdcl','apspdcl'],
        'gas': ['iocl','hpcl','bpcl'],
        'water': ['apwrd'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'assam': {
        'electricity': ['apdcl'],
        'gas': ['agcl'],
        'water': ['aphe'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'bihar': {
        'electricity': ['nbpdcl','sbpdcl'],
        'gas': ['gail'],
        'water': ['bphe'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'chhattisgarh': {
        'electricity': ['cspdcl'],
        'gas': ['gail'],
        'water': ['cphe'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'goa': {
        'electricity': ['ged'],
        'gas': ['iocl','hpcl','bpcl'],
        'water': ['pwd'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'gujarat': {
        'electricity': ['dgvcl','mgvcl','pgvcl','ugvcl'],
        'gas': ['ggl'],
        'water': ['gwssb'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'haryana': {
        'electricity': ['dhbvn','uhbvn'],
        'gas': ['hcgdl'],
        'water': ['phed'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'himachal_pradesh': {
        'electricity': ['hpsebl'],
        'gas': ['iocl','hpcl','bpcl'],
        'water': ['iph'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'jharkhand': {
        'electricity': ['jbvnl'],
        'gas': ['gail'],
        'water': ['jphe'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'karnataka': {
        'electricity': ['bescom','mescom','hescom','gescom','cescom'],
        'gas': ['gail'],
        'water': ['bwssb'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'kerala': {
        'electricity': ['kseb'],
        'gas': ['ioagpl'],
        'water': ['kwa'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'madhya_pradesh': {
        'electricity': ['mppgcl','mpptcl','mppkvvcl','mpmkvvcl','mppkvvcl'],
        'gas': ['gail'],
        'water': ['mpudc'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'maharashtra': {
        'electricity': ['msedcl','tpc','aeml'],
        'gas': ['mgl'],
        'water': ['mmrda'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'manipur': {
        'electricity': ['mspdcl'],
        'gas': ['iocl','hpcl','bpcl'],
        'water': ['phed'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'meghalaya': {
        'electricity': ['mepdcl'],
        'gas': ['iocl','hpcl','bpcl'],
        'water': ['phed'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'mizoram': {
        'electricity': ['p&e'],
        'gas': ['iocl','hpcl','bpcl'],
        'water': ['phed'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'nagaland': {
        'electricity': ['dop'],
        'gas': ['iocl','hpcl','bpcl'],
        'water': ['phed'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'odisha': {
        'electricity': ['tpnodl','tpsodl','tpcodl','tpwodl'],
        'gas': ['gail'],
        'water': ['pheo'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'punjab': {
        'electricity': ['pspcl'],
        'gas': ['gail'],
        'water': ['pwssb'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'rajasthan': {
        'electricity': ['jvvnl','avvnl','jdvvnl'],
        'gas': ['rsgl'],
        'water': ['phed'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'sikkim': {
        'electricity': ['sikkim power'],
        'gas': ['iocl','hpcl','bpcl'],
        'water': ['phed'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'tamil_nadu': {
        'electricity': ['tangedco'],
        'gas': ['iocl'],
        'water': ['cmwssb'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'telangana': {
        'electricity': ['tsspdcl','tsnpdcl'],
        'gas': ['bgl'],
        'water': ['hmwssb'],
        'mobile': ['airtel','bsnl','jio','vi']
    }
}

billDB = {
    # Andhra Pradesh
    2001: {'Customer Name': 'Ravi Teja', 'service provider': 'apepdcl', 'unit': 42, 'Amount': 550, 'Due Date': '15/04/2025', 'status': 'Unpaid', 'service': 'electricity', "state": "andhra pradesh"},
    2002: {'Customer Name': 'Divya Reddy', 'service provider': 'hpcl', 'Amount': 1050, 'Due Date': '18/07/2025', 'status': 'Unpaid', 'service': 'gas', "state": "andhra pradesh"},
    2003: {'Customer Name': 'Manoj Kumar', 'service provider': 'apwrd', 'Amount': 700, 'Due Date': '10/11/2025', 'status': 'Unpaid', 'service': 'water', "state": "andhra pradesh"},
    2004: {'Customer Name': 'Sita Devi', 'service provider': 'airtel', 'Amount': 499, 'Due Date': '05/05/2026', 'status': 'Unpaid', 'service': 'mobile', "state": "andhra pradesh"},

    # Telangana
    2021: {'Customer Name': 'Arun Reddy', 'service provider': 'tsspdcl', 'unit': 50, 'Amount': 620, 'Due Date': '12/05/2025', 'status': 'Paid', 'service': 'electricity',"state": "telangana"},
    2022: {'Customer Name': 'Meena Rao', 'service provider': 'bgl', 'Amount': 1150, 'Due Date': '15/08/2025', 'status': 'Unpaid', 'service': 'gas', "state": "Telangana"},
    2023: {'Customer Name': 'Ramesh Goud', 'service provider': 'hmwssb', 'Amount': 760, 'Due Date': '18/10/2025', 'status': 'Unpaid', 'service': 'water', "state": "telangana"},
    2024: {'Customer Name': 'Priya Nair', 'service provider': 'airtel', 'Amount': 699, 'Due Date': '25/07/2026', 'status': 'Unpaid', 'service': 'mobile', "state": "telangana"},

    # Odisha
    2025: {'Customer Name': 'Deepak Mohanty', 'service provider': 'tpnodl', 'unit': 45, 'Amount': 590, 'Due Date': '22/06/2025', 'status': 'Paid', 'service': 'electricity', "state": "odisha"},
    2026: {'Customer Name': 'Kavita Das', 'service provider': 'gail', 'Amount': 1120, 'Due Date': '28/08/2025', 'status': 'Unpaid', 'service': 'gas', "state": "odisha"},
    2027: {'Customer Name': 'Sanjay Pattnaik', 'service provider': 'pheo', 'Amount': 830, 'Due Date': '30/12/2025', 'status': 'Unpaid', 'service': 'water', "state": "odisha"},
    2028: {'Customer Name': 'Sneha Mishra', 'service provider': 'bsnl', 'Amount': 649, 'Due Date': '15/09/2026', 'status': 'Unpaid', 'service': 'mobile', "state": "odisha"},

    # Tamil Nadu
    2033: {'Customer Name': 'Vikram Iyer', 'service provider': 'tangedco', 'unit': 55, 'Amount': 750, 'Due Date': '20/08/2025', 'status': 'Paid', 'service': 'electricity', "state": "tamil nadu"},
    2034: {'Customer Name': 'Lakshmi Raman', 'service provider': 'hpcl', 'Amount': 1180, 'Due Date': '25/10/2025', 'status': 'Unpaid', 'service': 'gas', "state": "tamil nadu"},
    2035: {'Customer Name': 'Rajeshwari M', 'service provider': 'cmwssb', 'Amount': 890, 'Due Date': '05/12/2025', 'status': 'Paid', 'service': 'water', "state": "tamil nadu"},
    2036: {'Customer Name': 'Suresh Kumar', 'service provider': 'jio', 'Amount': 799, 'Due Date': '30/11/2026', 'status': 'Unpaid', 'service': 'mobile', "state": "tamil nadu"},

    # Maharashtra
    2041: {'Customer Name': 'Amit Joshi', 'service provider': 'mseb', 'unit': 52, 'Amount': 730, 'Due Date': '10/06/2025', 'status': 'Unpaid', 'service': 'electricity', "state": "maharashtra"},
    2042: {'Customer Name': 'Neha Deshmukh', 'service provider': 'mgl', 'Amount': 1190, 'Due Date': '18/09/2025', 'status': 'Unpaid', 'service': 'gas', "state": "maharashtra"},
    2043: {'Customer Name': 'Rohit Patil', 'service provider': 'mmrda', 'Amount': 920, 'Due Date': '28/11/2025', 'status': 'Unpaid', 'service': 'water', "state": "maharashtra"},
    2044: {'Customer Name': 'Pooja Sharma', 'service provider': 'vodafone', 'Amount': 699, 'Due Date': '05/10/2026', 'status': 'Unpaid', 'service': 'mobile', "state": "maharashtra"},

    # More states added here following the same format...
}

# This ensures the user isn't asked repeatedly for their language
@tool
def set_language(user_input: str):
    """
    Sets the user's language preference.
    Accepts 'English', 'Hindi', 'Telugu', 'odia', 'tamil', 'marathi', or 'bangali'.
    """
    print("Inside set_language")

    valid_languages = ["english", "hindi", "telugu", "tamil", "marathi","odia","bangali"]

    if user_input.lower() in valid_languages:
        return f"Language set to {user_input}. Please provide the state in India where the bill is related."

    return "Invalid choice. Please select a language: English, Hindi, Telugu, Odia, Tamil, Marathi, or Bengali."

# This prevents issues like "Canada" being accepted.
@tool
def validate_state(user_input: str):
    """
    Validates if the user has provided a valid state in India.
    """
    print("Inside validate_state tool")
    user_input = user_input.title().strip()  # Normalize input

    if user_input in stateDB:
        return "Please select your biller category: For an example electricity, water, or gas."

    return "Currently, we supports bill payments only in India. Please enter a valid Indian state."

@tool
def validate_biller_category(biller_category: str):
    """
    Validates if the user provided a valid biller category supported by VoxPay

    Args:
        biller_category (str): The biller category name provided by the user.
    """
    print("Inside validate_biller_category tool")

    biller_category = biller_category.title().strip().lower()  # Normalize input

    if biller_category in billerCategoryDB:
        return "Please provide your service provider name."
    else: return f"Currently, we are not supporting {biller_category} biller category. Please enter another biller category name to proceed with."

@tool
def validate_service_provider(biller_category: str, state: str, service_provider: str):
    """
    Fetches a list of service providers based on the user's biller_category, state and bill service provide name and validate the service provider.
    """
    print(f"Inside validate_service_provider tool:  biller_category: '{biller_category}' state: '{state}', service_provider: '{service_provider}'")
    #if not state or not biller_category:
        #return "Please specify both the state and the biller category to validate the service providers."

    state = state.strip().lower()
    biller_category = biller_category.strip().lower()
    service_provider = service_provider.lower()

    #if state not in serviceDB:
        #return f"Sorry, I couldn't find service providers for the state. Please check the service provider."

    if biller_category not in serviceDB[state]:
        return f"Sorry, there are no listed providers for the biller category and service provider state."

    available_providers = serviceDB[state][biller_category]

    if service_provider:
        service_provider = service_provider.strip()
        if service_provider in available_providers:
            return f"Please provide your Consumer Number"
        else:
            return f"'{service_provider}' is not a valid service provider. Please enter a valid service provider name."

    #return f"The available service providers for '{biller_category}' in '{state}' are: {', '.join(available_providers)}."

# The system won’t assume "2025" is incorrect—it will ask for confirmation.
@tool
def validate_consumer_number(consumer_number: int):
    """
    Ensures the provided consumer number is valid.
    Args:
        consumer_number (int): The consumer number provided by the user.
    """
    print(f"Inside validate_consumer_number tool '{consumer_number}'")
    #if re.match(r"^(19|20)\d{2}$", user_input):
        #return f"It seems like you've entered {user_input}. Is this your actual consumer number? (yes/no)"
    if not consumer_number: return "please provide a valid consumer number."

    else: return "Fetching your bill details."


# Tool to fetch bill details based on consumer number
@tool
def fetch_bill_details(consumer_number: int, service_provider: str) -> str:
    """
    Fetches bill details based on consumer number and service provider name.
    Args:
        consumer_number (int): The user's consumer number.
        service_provider (str): The service provider name.
    Returns:
        str: A message containing the bill amount or an appropriate error message.
    """
    print("Inside fetch_bill_details tool")
    # Check if both provider and bill number are provided
    #if not consumer_number or not service_provider:
        #return "Please provide the consumer number and service provider name to fetch bill details."

    # Check if the consumer  number exists in the provider's record in billDB
    if consumer_number not in billDB:
        assert "BillNum Err"
        return f"Invalid consumer number. Please double-check your bill number."

    # Fetch and return the bill amount
    bill_details = billDB[consumer_number]
    return f"The status of consumer number: {consumer_number} of {bill_details['service']} utility is {bill_details['status']} for rupees {bill_details['Amount']} due {bill_details['Due Date']}. To confirm, you would like to proceed with the payment? If yes, please enter your UPI pin to authenticate the payment request."

@tool
#def process_bill_payment(biller_category: str, service_provider: str, state: str, consumer_number: str, amount: float, upi_pin: str) -> str:
def process_bill_payment() -> str:
    """
    Processes the bill payment for the given biller category.
    Returns:
        str: A message indicating whether the bill payment was successful or failed.
    """
    print("Inside process_bill_payment tool")

    return "Bill payment Successful."

# This avoids forcing the user to restart the process after paying one bill.
#@tool
def post_payment_navigation():
    """
    Provides options to the user after successful payment.
    """

    print("Inside post_payment_navigation tool")
    return "Payment successful! Would you like to: \n" \
           "1️. Pay another bill (same service, different provider/consumer number)\n" \
           "2️. Choose a different utility type\n" \
           "3️. Exit"

# Function to Get Current Time Greeting (from first version)
#@tool
def get_greeting():
    """Return a time-based greeting."""
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 15:
        return "Good noon"
    elif 15 <= current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

tools = [set_language, validate_state, validate_biller_category, validate_service_provider, validate_consumer_number, fetch_bill_details, process_bill_payment]
toolsMap = {"set_language": set_language, "validate_state": validate_state, "validate_biller_category": validate_biller_category, "validate_service_provider": validate_service_provider, "validate_consumer_number": validate_consumer_number, "fetch_bill_details": fetch_bill_details,"process_bill_payment" : process_bill_payment, "post_payment_navigation": post_payment_navigation}
llmTool = llm.bind_tools(tools)


def event():
    LANGUAGE = input(
        f"{get_greeting()}! I’m VoxPay, your personal bill payment assistance. I am here to help you with your bill payment.\nKindly mention the language you want to converse in (English, Hindi, Telugu):\n -->")

    memory = [SystemMessage(content=initialSystemMessage1), HumanMessage(content=f"I've chosen {LANGUAGE}. Let's start my payment process.")]
    # memory = [SystemMessage(content = initialSystemMessage2)]

    #tools = [set_language,validate_service_provider, fetch_bill_details]
   # toolsMap = {"validate_service_provider": validate_service_provider, "fetch_bill_details": fetch_bill_details}

    #llmService = llm
   # llmTool = llm.bind_tools(tools)

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

