
consumerDB = {
    '2037a': {
        'customer name': 'rajesh shetty',
        'state': 'odisha',
        'electricity': {'serviceCode':7412, 'service_provider': 'cesu', 'unit': 48, 'amount': 710, 'due date': '25/06/2025', 'status': 'paid'},
        'mobile': {'service': 4730, 'service_provider': 'airtel', 'amount': 599, 'due date': '15/08/2025', 'status': 'unpaid'}
    },
    '2045a': {
        'customer name': 'pradeep kumar',
        'state': 'karnataka',
        'electricity': {'service': 3591, 'service_provider': 'mescom', 'unit': 55, 'amount': 840, 'due date': '10/07/2025', 'status': 'unpaid'},
        'mobile': {'service': 4730, 'service_provider': 'airtel', 'amount': 710, 'due date': '30/09/2025', 'status': 'paid'},
        'gas': {'service': 5123, 'service_provider': 'gail', 'amount': 1200, 'due date': '05/07/2025', 'status': 'paid'}
    },
    '2052a': {
        'customer name': 'anita singh',
        'state': 'telangana',
        'electricity': {'service': 8021, 'service_provider': 'tsspdcl', 'unit': 65, 'amount': 950, 'due date': '20/07/2025', 'status': 'unpaid'},
        'mobile': {'service': 9651, 'service_provider': 'jio', 'amount': 850, 'due date': '25/08/2025', 'status': 'paid'},
        'gas': {'service': 5283, 'service_provider': 'hmwssb', 'amount': 350, 'due date': '28/06/2025', 'status': 'unpaid'}
    },
    '2061a': {
        'customer name': 'suresh rao',
        'state': 'odisha',
        'electricity': {'service': 7412, 'service_provider': 'cesu', 'unit': 72, 'amount': 1050, 'due date': '12/07/2025', 'status': 'paid'},
        'mobile': {'service': 9651, 'service_provider': 'jio', 'amount': 699, 'due date': '05/09/2025', 'status': 'unpaid'}
    }
}


# Importing necessary packages
import json

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from langchain.callbacks import get_openai_callback

# from databases import *

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
- You should always think about what to do, do not use any tool if it is not needed.
- NEVER call tools or proceed to the next step until you have collected all required information from the user.
- Ask ONE question at a time, wait for the user’s response, and store it before moving forward.
- Output ONLY the response for the current step, nothing else.
- Do NOT repeat earlier messages or include examples unless explicitly asked.
- Do NOT assume any information (e.g. service providers) and do NOT mask the numbers.  Do not make any assumptions.
- Follow this EXACT sequence:

### Step-by-Step Process:
1. Greet the user with: "I’m VoxPay, your personal bill payment assistance. I am here to help you with your bill payment."
2. After that, say: "To help with your bill payments, please provide the utility service you want to pay for". This is the service.
4. Ask the user their consumer number, say: "Please provide your consumer number". This is the consumer_number.
5. After the consumer_number is provided, with the help of service and consumer_number, fetch the bill using the fetch_bill_details tool. Display every detail. say: "Thanks for providing the details. Hold on! I am fetching your bill details."
6. Display the consumer number, Customer Name, bill amount, due date, and service provider name in a single statement. say: "Do you want me to pay yor bill. If yes please enter your UIP pin"
7. Confirm payment. Say: Your bill payment has been successfully processed.

### Additional Rules:
- If the user provides incomplete or unclear input (e.g., misspelled state), ask for clarification instead of guessing.
- Do not mention utility service providers until the user specifies the utility category.
- Once bill paid you should remember only selected state name, incase your want to pay any other bill.
'''

initialSystemMessage3 = f'''You are VoxPay, a conversational payment assistant EXCLUSIVELY in India. Speak in {LANGUAGE}
### General Rules:
- NEVER call tools or proceed to the next step until you have collected all required information from the user.
- Ask ONE question at a time, wait for the user’s response, and store it before moving forward.
- Output ONLY the response for the current step, nothing else.
- Strictly do NOT repeat earlier messages or include examples unless explicitly asked.
- Do NOT assume any information (e.g. service providers) and do NOT mask the numbers.  Do not make any assumptions. Do not deviate.
- Follow this EXACT sequence. Do not explicitly mention it to the user:

### Step-by-Step Process:
1. Start with greeting the user.
2. After the user responds, ask the user to  provide the utility service they to pay for. This is the service.
4. After getting the service, ask the user their consumer number. This is the consumer_number.
5. After the consumer_number is provided, with the help of service and consumer_number, fetch the bill using the fetch_bill_details tool. Display the consumer number, Customer Name, bill amount, due date, and service provider name in a single statement.
6. Only after ask the user if they want to pay the bill. Ask: "Do you want me to pay your bill. If yes please enter your UIP pin"
7. Confirm payment. Say: Your bill payment has been successfully processed.

### Additional Rules:
- Do not hallucinate.
- If the user provides incomplete or unclear input (e.g., misspelled state), ask for clarification instead of guessing.
- Do not mention utility service providers until the user specifies the utility category.
- Once bill paid you should remember only selected state name, incase your want to pay any other bill.
'''


# Tool to fetch bill details based on consumer number
@tool
def fetch_bill_details(consumer_number: str, service: str) -> str:
    """
    Tool to fetches bill details based on consumer number and .
    Args:
        consumer_number (str): The user's consumer number.
        service (str): The service the user wants to pay the bill for. 
    Returns:
        str: A message containing the bill amount or an appropriate error message.
    """
    # Check if both provider and bill number are provided
    if not consumer_number or not service or consumer_number=='' or service=='':
        return "Please provide the consumer number and service to fetch bill details."

    if consumer_number.lower() not in consumerDB:

        return "No bills linked to the provided consumer were found in the database."


    # Fetch and return the bill amount
    bill_details = consumerDB[consumer_number.lower()]

    if service not in bill_details:
        return f"No bills linked to the {service} for the consumer were found in the database."
    # print(bill_details[service.lower()])

    return f"The status of consumer {bill_details['customer name']} number: {consumer_number} of {service} utility is {bill_details[service.lower()]}"
    

def event():

    LANGUAGE = input("Kindly mention the langauage you want to converse in (English, Hindi, Telugu):\n -->")

    memory = [SystemMessage(content = initialSystemMessage2.format(LANGUAGE)), HumanMessage(content='Start my payment process.')]
    memory = [SystemMessage(content = initialSystemMessage3.format(LANGUAGE))]


    tools = [fetch_bill_details]
    toolsMap = {"fetch_bill_details":fetch_bill_details}

    llmTool = llm.bind_tools(tools)

    firstInteraction = False

    while True:
        userInput = input("User Input:\n -->").lower()
        if userInput == '/end':
            break
        memory.append(HumanMessage(content=userInput))
        if firstInteraction:
            firstInteraction = False
            aiMsg = llm.invoke(memory)
        else:
            aiMsg = llmTool.invoke(memory)

        if aiMsg.tool_calls:
            for toolCall in aiMsg.tool_calls:
                if toolCall['name'] in toolsMap:
                    toolMsg = toolsMap[toolCall['name']].invoke(toolCall)
                    memory.append(toolMsg)
            aiMsg = llmTool.invoke(memory)
        print(f"AI Response:\n--> {aiMsg.content}\n")

        
try:
    with get_openai_callback() as cb:
        event()
        print("Total Tokens Used in transaction: ", cb.total_tokens)
except Exception as e:
    print(f"ERR: {e}")

# script = ['Hello', "I live in Odisha", "I want to pay my gas bill", "My service provider is OGAS1 and my bill number is 123a4"]


