# Importing necessary packages
import json

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Importing model
llm = ChatOllama(model="llama3.2", temperature=0)

initialSystemMessage = '''You are an excellent virtual assistant. Your name is PayLLM. In the first user interaction, respond directly without calling any tools.
You should strictly follow the following steps:
0. Ask the user if they want to pay any bill.
1. Ask the user the state they are in.
2. Ask the user my service provider.
3. Ask the user the bill number.
4. Ask the user if you should fetch the bill details.
5. Inform the user the bill details once fetched.
6. Ask the user if you should pay the bill.
7. Is the user agrees, pay the bill.

Ask these questions one at a time and store in your memory. Dont expect all at once. Fetch the bill only if you have all this information.
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

initialSystemMessage = '''You are a helpful assistant guiding the user through a bill payment process. Ask the user for the following information in order:

1. **State of residence**: Ask the user for their state of residence to determine where they are located.
   Example: "What is your state of residence? (e.g., California, New York, Telangana, etc.)"

2. **Service provider**: After the state is provided, ask the user for their service provider, such as the company they are paying a bill to.
   Example: "Which service provider would you like to pay? (e.g., electricity, water, internet, Comcast, etc.)"

3. **Bill number**: After the service provider is mentioned, ask the user to provide their bill number for identification.
   Example: "Please provide your bill number."

4. **Confirmation to fetch and pay**: Once the bill number is provided, ask the user if they would like to fetch the bill details and proceed with payment.
   Example: "Would you like me to fetch the bill amount and proceed with payment? (yes/no)"

The assistant should **never mention errors** or missing bill details in the flow. Just continue with the prompts until all necessary information is gathered.

---

**Example of a smooth conversation flow**:

1. **Assistant**: "What is your state of residence? (e.g., California, New York, Telangana, etc.)"
2. **User**: "Telangana"
3. **Assistant**: "Which service provider would you like to pay? (e.g., electricity, water, internet, Comcast, etc.)"
4. **User**: "Airtel"
5. **Assistant**: "Please provide your bill number."
6. **User**: "123456"
7. **Assistant**: "Would you like me to fetch the bill amount and proceed with payment? (yes/no)"
8. **User**: "Yes"
9. **Assistant**: "Fetching bill details... The bill amount is $100. Your payment of $100 is ready. Please provide your payment details."
'''



billDB = {
    9182:{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':32,'Amount':341, "Due Date":'10/01/2025', 'status':'Paid', 'service':'Electricity'},
    1928:{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':37,'Amount':547, "Due Date":'11/02/2025','status':'Unpaid', 'service':'Electricity'},
    1038:{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':23,'Amount':298, "Due Date":'09/10/2025','status':'Paid', 'service':'Electricity'},
    8321 :{'Customer Name':'Asutosh Dalei','service provider':'Airtel','Amount':1008, "Due Date":'04/03/2025', 'status':'Paid', 'service':'WiFi'},
    1008:{'Customer Name':'Asutosh Dalei','service provider':'Airtel','Amount':1276, "Due Date":'04/02/2025','status':'Paid', 'service':'WiFi'},
    1035:{'Customer Name':'Asutosh Dalei','service provider':'Airtel','Amount':1932, "Due Date":'08/04/2025','status':'Unpaid', 'service':'WiFi'}
}


@tool
def payBill(billNumber: int) -> str:
    """Function to pay bill using bill number.
    Args:
        billNumber: Bill Number (String). Output: Bill paid status
    """
    if billNumber not in billDB:
        return "Bill Details not found."
    if billDB[billNumber]['status'] == 'Paid':
        return "Bill paid already"
    billDB[billNumber]['status'] = 'Paid'
    return "Bill paid successfully"

@tool
def fetchBill(billNumber):
    """
    Function to fetch bill details using bill number. Input: Bill Number. Output: Bill Amount, Bill Details
    Args:
        billNumber: Bill Number
    """
    try:
        return json.dumps(billDB[billNumber])
    except:
        return "Bill not found"
    
serviceTools = [fetchBill,payBill]
serviceToolsMap = {"fetchBill":fetchBill, "payBill": payBill}

# @tool
def event(llm):
    '''
    Payment Event
    '''
    serviceMessages = [SystemMessage(content = initialSystemMessage), HumanMessage(content='Start my payment process.')]
    llmService = llm
    aiMsgSer = llmService.invoke(serviceMessages)
    firstInteraction = True
    while True:
        if firstInteraction:
            print(f"AI Response:\n --> {aiMsgSer.content}")
            firstInteraction = False
            llmService = llm.bind_tools(serviceTools)

        if aiMsgSer.tool_calls:
            for toolCallSer in aiMsgSer.tool_calls:
                toolSelected = serviceToolsMap[toolCallSer['name']]
                toolMsg = toolSelected.invoke(toolCallSer)
                serviceMessages.append(toolMsg)
            aiMsgSer = llmService.invoke(serviceMessages)
            serviceMessages.append(aiMsgSer)
            print(f"AI Response:\n --> {aiMsgSer.content}")
            continue
        userInput = input("User Input:\n -->")
        if userInput == "/end":
            break
        serviceMessages.append(HumanMessage(content = userInput))
        aiMsgSer = llmService.invoke(serviceMessages)
        if aiMsgSer.content != '':
            print(f"AI Response:\n--> {aiMsgSer.content}")
        serviceMessages.append(HumanMessage(content = userInput))

try:
    event(llm)
except Exception as e:
    print('ERR',e)