# Importing necessary packages
import json
import re

import datetime
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from databases import *

# Importing model
llm = ChatOllama(model="llama3.2:latest", temperature=0)

LANGUAGE = 'english'
initialSystemMessage1 = f'''You are VoxPay, a conversational payment assistant EXCLUSIVELY in India.
### General Rules:
- NEVER call tools or proceed to the next step until you have collected all required information from the user.
- Ask ONE question at a time, wait for the user’s response, and store it before moving forward.
- Output ONLY the response for the current step, nothing else.
- Do NOT repeat earlier messages or include examples unless explicitly asked.
- Do NOT assume any information (e.g. service providers) and do NOT mask the numbers.  
- Follow this EXACT sequence:

### Step-by-Step Process:
1. Greet the user with: "I’m VoxPay, your personal bill payment assistance. I am here to help you with your bill payment. Kindly mention the language you want to converse in (English, Hindi, Telugu)."
2. After the user selects a language, say: "You have chosen [LANGUAGE]. To help with your bill payments, please provide your state in India where the bill is related."
3. After the state is provided, say: "please provide your utility category? Options are: electricity, water, or gas."
4. After the utility category is provided, say: "Please provide your service provider name."
5. After the service provider is provided, Ask the user for their consumer number. say: "Please provide your consumer number."
6. After the consumer number is provided, with the help of service provider name and consumer number, fetch the bill. say: "Thanks for providing the details. Hold on! I am fetching your bill details."
7. Display the consumer number, Customer Name, bill amount, due date, and service provider name in a single statement. say: "Do you want me to pay yor bill. If yes please enter your UIP pin"
8. Confirm payment. Say: Your bill payment has been successfully processed.

### Additional Rules:
- If the user provides incomplete or unclear input (e.g., misspelled state), ask for clarification instead of guessing.
- Do not mention utility service providers until the user specifies the utility category.
- Once bill paid you should remember only selected state name, incase your want to pay any other bill.
'''

initialSystemMessage2 = f'''You are VoxPay, a conversational payment assistant EXCLUSIVELY in India. Speak in {LANGUAGE}
### General Rules:
- NEVER call tools or proceed to the next step until you have collected all required information from the user.
- Ask ONE question at a time, wait for the user’s response, and store it before moving forward.
- Output ONLY the response for the current step, nothing else.
- Do NOT repeat earlier messages or include examples unless explicitly asked.
- Do NOT assume any information (e.g. service providers) and do NOT mask the numbers.  Do not make any assumptions.
- Follow this EXACT sequence:

### Step-by-Step Process:
1. Greet the user with: "I’m VoxPay, your personal bill payment assistance. I am here to help you with your bill payment."
2. After the user selects a language, say: "You have chosen [LANGUAGE]. To help with your bill payments, please provide your state in India where the bill is related."
3. After the state is provided, ask the user about the utility they want to pay for. say: "please provide your utility category?"
4. Call the fetch_service_provider tool to get the list of service providers related to the particular state and utility. Tell the list to the user only after calling the tool.
5. Ask the user their service provider, say: "Please provide your service provider name."
6. Ask the user their consumer number, say: "Please provide your consumer number."
7. After the consumer number is provided, with the help of service provider name and consumer number, fetch the bill. Display every detail. say: "Thanks for providing the details. Hold on! I am fetching your bill details."
8. Display the consumer number, Customer Name, bill amount, due date, and service provider name in a single statement. say: "Do you want me to pay yor bill. If yes please enter your UIP pin"
9. Confirm payment. Say: Your bill payment has been successfully processed.

### Additional Rules:
- If the user provides incomplete or unclear input (e.g., misspelled state), ask for clarification instead of guessing.
- Do not mention utility service providers until the user specifies the utility category.
- Once bill paid you should remember only selected state name, incase your want to pay any other bill.
'''



#State database  for state validation
stateDB = {'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'}

utilityServiceDB = {'electricity', 'gas', 'water','mobile'}

# service provider Database based on states

# This ensures the user isn't asked repeatedly for their language
@tool
def set_language(user_input: str):
    """
    Sets the user's language preference.
    Accepts 'English', 'Hindi', 'Telugu', 'odia', 'tamil', 'marathi', or 'bengali'.
    """
    valid_languages = ["english", "hindi", "telugu", "tamil", "marathi","odia","bengali"]

    if user_input.lower() in valid_languages:
        return f"Language set to {user_input}. Please provide the state in India where the bill is related."

    return "Invalid choice. Please select a language: English, Hindi, Telugu, Odia, Tamil, Marathi, or Bengali."

# This prevents issues like "Canada" being accepted.
@tool
def validate_state(user_input: str):
    """
    Validates if the user has provided a valid state in India.
    """
    user_input = user_input.title().strip()  # Normalize input

    if user_input in stateDB:
        return f"State set to {user_input}. Please select a utility type: Electricity, Water, or Gas."

    return "Currently, VoxPay supports bill payments only in India. Please enter a valid Indian state."

@tool
def validate_utility_category_type(utility_name: str):
    """
    Validates if the given service is supported by VoxPay.

    Args:
        utility_name (str): The utility service name provided by the user.
    """
    utility_name = utility_name.title().strip().lower()  # Normalize input

    if utility_name in utilityServiceDB:
        return f"You have chose {utility_name}. Please provide your service provider name."

    return f"Currently, VoxPay is not supporting {utility_name} category. Please enter another utility service name to proceed with."

# The system won’t assume "2025" is incorrect—it will ask for confirmation.
@tool
def validate_consumer_number(user_input):
    """
    Ensures the provided consumer number is valid.
    If the number looks like a year (e.g., 2025), asks for confirmation.
    """
    #if re.match(r"^(19|20)\d{2}$", user_input):
        #return f"It seems like you've entered {user_input}. Is this your actual consumer number? (yes/no)"

    return f"Consumer number {user_input} received. Fetching your bill details..."


@tool
def fetch_service_provider(service: str, state: str) -> str:
    """
    Fetches a list of service providers based on the user's state and bill service.
    Also validates if a given service provider is valid for the state and service.

    Args:
        service (str): The type of service for which the user wants to pay the bill.
        state (str): The state of residence of the user.
    Returns:
        str (str): A message containing either the list of service providers or a validation result.
    """
    if not state or not service:
        return "Please specify both the state and the service type to fetch providers."

    state = state.strip().lower()
    service = service.strip().lower()

    if state not in serviceDB:
        return f"Sorry, I couldn't find service providers for '{state}'. Please check the state name."

    if service not in serviceDB[state]:
        return f"Sorry, there are no listed providers for '{service}' in '{state}'."


    available_providers = serviceDB[state][service]


    if False:
        provider = provider.strip()
        if provider in available_providers:
            return f"'{provider}' is a valid service provider for '{service}' in '{state}'."
        else:
            return f"'{provider}' is not a valid service provider for '{service}' in '{state}'. Available providers: {', '.join(available_providers)}."
    return f"The available service providers for '{service}' in '{state}' are: {available_providers}."
    return f"The available service providers for '{service}' in '{state}' are: {', '.join(available_providers)}."


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
    # Check if both provider and bill number are provided
    if not consumer_number or not service_provider:
        return "Please provide the consumer number and service provider name to fetch bill details."

    # Check if the consumer  number exists in the provider's record in billDB
    if consumer_number not in billDB:
        assert "BillNum Err"
        return f"Invalid consumer number '{consumer_number}'. Please double-check your bill number."

    # Fetch and return the bill amount
    bill_details = billDB[consumer_number]
    return f"The status of consumer number: {consumer_number} of {bill_details['service']} utility is {bill_details['status']} for rupees {bill_details['Amount']} due {bill_details['Due Date']}. To confirm, you would like to proceed with the payment? If yes, please enter your UPI pin to authenticate the payment request."

@tool
def process_bill_payment(service: str, provider: str, state: str, consumer_number: str, amount: float, upi_pin: str) -> str:
    """
    Processes the bill payment for the given utility service.

    Args:
        service (str): The utility service type (electricity, gas, water, mobile).
        provider (str): The service provider name.
        state (str): The state in India where the bill applies.
        consumer_number (str): The consumer ID or bill account number.
        amount (float): The bill amount.
        upi_pin (str): The UPI PIN for authentication.

    Returns:
        str: A message indicating whether the bill payment was successful or failed.
    """

    # Validate the service type
    if service.lower() not in utilityServiceDB:
        return f"'{service}' is not a valid utility service. Please choose from {', '.join(utilityServiceDB)}."

    # Validate required details
    if not (provider and state and consumer_number and amount and upi_pin):
        return "Missing required details. Please provide service, provider, state, consumer number, amount, and UPI PIN."

    # Simulate payment success/failure
    validation_sucess = True
    #payment_success = random.choice([True, False])

    if validation_sucess:
        return f"Bill payment of ₹{amount:.2f} for {service} with {provider} (Consumer No: {consumer_number}) in {state} was successful! Would you like to:  \nPay another bill (same service, different provider/consumer number) \nChoose a different utility type\n"
    else:
        return f"Bill payment failed. Please check your details and try again."

# This avoids forcing the user to restart the process after paying one bill.
@tool
def post_payment_navigation():
    """
    Provides options to the user after successful payment.
    """
    return '''Payment successful! Would you like to:
           1️. Pay another bill (same service, different provider/consumer number)
           2️. Choose a different utility type
           3️. Exit'''

# Function to Get Current Time Greeting (from first version)
# @tool
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

tools = [validate_state, validate_utility_category_type, validate_consumer_number, fetch_service_provider, fetch_bill_details,process_bill_payment,
             post_payment_navigation]
toolsMap = {"validate_state": validate_state, "validate_utility_category_type": validate_utility_category_type,
                "validate_consumer_number": validate_consumer_number, "fetch_service_provider": fetch_service_provider,
                "fetch_bill_details": fetch_bill_details,"process_bill_payment" : process_bill_payment, "post_payment_navigation": post_payment_navigation}
llmTool = llm.bind_tools(tools)


def event():
    LANGUAGE = input(
        f"{get_greeting()}! I’m VoxPay, your personal bill payment assistance. I am here to help you with your bill payment.\nKindly mention the language you want to converse in (English, Hindi, Telugu):\n -->")

    memory = [SystemMessage(content=initialSystemMessage2.format(LANGUAGE))]
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

def event2():
    LANGUAGE = input(f"{get_greeting()}! I’m VoxPay, your personal bill payment assistance. I am here to help you with your bill payment.\nKindly mention the language you want to converse in (English, Hindi, Telugu):\n -->")

    memory = [SystemMessage(content=initialSystemMessage1), HumanMessage(content=f"Hello! I want to speak in {LANGUAGE}. Let's start my payment process.")]

    aiMsg = llmTool.invoke(memory)
    print(f"AI Response:\n--> {aiMsg.content}\n")

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
        memory.append(aiMsg)


def eventScript():
    # LANGUAGE = input(f"{get_greeting()}! I’m VoxPay, your personal bill payment assistance. I am here to help you with your bill payment.\nKindly mention the language you want to converse in (English, Hindi, Telugu):\n -->")
    print(f"{get_greeting()}! I’m VoxPay, your personal bill payment assistance. I am here to help you with your bill payment.\nKindly mention the language you want to converse in (English, Hindi, Telugu):\n --> English")
    LANGUAGE = 'english'
    memory = [SystemMessage(content=initialSystemMessage1), HumanMessage(content=f"I've chosen {LANGUAGE}. Let's start my payment process.")]

    firstInteraction = True

    script = ['Hello', "I live in Karnataka", "I want to pay my electricity bill", "My service provider is BESCOM", "That is 2037"]
    for scr in script:
        print("User Input:\n -->", scr)
        userInput = scr.lower()
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
    # event2()
    # eventScript()
except Exception as e:
    print(f"ERR: {e}")






