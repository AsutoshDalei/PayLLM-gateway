# Importing necessary packages
import json

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from databases import *

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

    if state not in providerDB:
        return f"Sorry, I couldn't find service providers for '{state}'. Please check the state name."

    if service not in serviceDB[state]:
        return f"Sorry, there are no listed providers for '{service}' in '{state}'."

    # Fetch providers
    providers = serviceDB[state][service].keys()

    return f"The available service providers for '{service}' in '{state}' are: {', '.join(providers)}."

@tool
def validate_provider(service_provider: str, state: str, service: str):
    """
    Validates if service_provider is available or not.
    Args:
        state (str): The state of residence of the user.
        service (str): The type of service for which the user wants to pay the bill.
        service_provider (str): The service provider's name for the utility.
    Returns:
        str: If the service_provider is available in the database or the list of service provider's code (based on availability)
    """
    if not service_provider or not state or not service:
        return "INVALID_ARGS"
    
    if service_provider not in providerDB[state][service]:
        # return "The provided {service_provider} is not available."
        return 'False'
    return providerDB[state][service][service_provider]
    # return "The provided {service_provider} is available."

@tool
def validate_consumer(consumer_num: int):
    """
    Validates if the consumer_number is available or not.
    Args:
        consumer_num (str): The user's consumer number.
    Returns:
        str: If the consumer_number is available in the database or the dictionary of the consumer's bills and information.
    """
    if not consumer_num:
        return "INVALID_ARGS"
    if consumer_num not in consumerDB:
        return 'False'
    return consumerDB[consumer_num]


# Tool to fetch bill details based on consumer number
@tool
def fetch_bill_details(consumer_details: dict, service_provider: int) -> str:
    """
    Fetches bill details based on consumer number.
    Args:
        consumer_number (int): The user's consumer number.
        service_provider (str): The service provider's name for the utility. 
    Returns:
        str: A message containing the bill amount or an appropriate error message.
    """
    # Check if both provider and bill number are provided
    if not consumer_details or not service_provider:
        return "Please provide the consumer number and service provider's name to fetch bill details."

    if service_provider not in consumer_details:


    # Fetch and return the bill amount
    bill_details = billDB[consumer_number]
    return f"The status of consumer number: {consumer_number} of {bill_details['service']} utility is {bill_details['status']} for rupees {bill_details['Amount']} due {bill_details['Due Date']}"
    

def event():

    LANGUAGE = input("Kindly mention the langauage you want to converse in (English, Hindi, Telugu):\n -->")

    memory = [SystemMessage(content = initialSystemMessage2.format(LANGUAGE)), HumanMessage(content='Start my payment process.')]

    tools = [fetch_service_provider, validate_provider, validate_consumer]
    toolsMap = {"fetch_service_provider":fetch_service_provider, "validate_provider":validate_provider, 'validate_consumer':validate_consumer}


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
                if toolCall['name'] == 'validate_provider':
                    valProv = toolsMap[toolCall['name']].invoke(toolCall)
                    if valProv == "INVALID_ARGS":
                        memory.append(SystemMessage(content = "Tell the user that the input arguments are wrong. Ask them to correct them."))
                        # break
                    elif valProv == 'False':
                        memory.append(SystemMessage(content = "Tell the user that the service provider is unavailable. Ask them to correct them."))
                        # break
                    else:
                        memory.append(SystemMessage(content= f'The code for user\'s service provider is {valProv}.'))

                elif toolCall['name'] == 'validate_consumer':
                    valCons = toolsMap[toolCall['name']].invoke(toolCall)
                    if valCons == "INVALID_ARGS":
                        memory.append(SystemMessage(content = "Tell the user that the input arguments are wrong. Ask them to correct them."))
                        # break
                    elif valCons == 'False':
                        memory.append(SystemMessage(content = "Tell the user that the consumer number is unavailable. Ask them to correct them."))
                        # break
                    else:
                        memory.append()



                elif toolCall['name'] in toolsMap:
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


