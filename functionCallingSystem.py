# Importing necessary packages
import json

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Importing model
llm = ChatOllama(model="llama3.2", temperature=0)

mockElectricityBills = {
    "9182":{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':32,'Amount':341, "Due Date":'10/01/2025', 'status':'Paid'},
    "1928":{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':37,'Amount':547, "Due Date":'11/02/2025','status':'Unpaid'},
    "1038":{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':23,'Amount':298, "Due Date":'09/10/2025','status':'Paid'}
}

mockWifiBills = {
    "8321":{'Customer Name':'Asutosh Dalei','service provider':'Airtel','Amount':1008, "Due Date":'04/03/2025', 'status':'Paid'},
    "1928":{'Customer Name':'Asutosh Dalei','service provider':'Airtel','Amount':1276, "Due Date":'04/02/2025','status':'Paid'},
    "1038":{'Customer Name':'Asutosh Dalei','service provider':'Airtel','Amount':1932, "Due Date":'08/04/2025','status':'Unpaid'}
}

class BillPay():
    def __init__(self, service, llm, billDB):
        serviceTools = []
        self.service = service
        self.llmService = llm.bind_tools(serviceTools)

        self.userDetails = fetchUserDetails()
        self.billDB = billDB

    @tool
    def fetchBill(self, billNumber):
        """Function to fetch bill details using bill number. Input: Bill Number. Output: Bill Amount, Bill Details"""
        # This is a mock setup, for the sole purpose of testing the system.
        return json.dumps(self.billDB[billNumber])
    
    def payBill(self, billNumber):
        """Function to pay bill using bill number. Input: Bill Number. Output: Bill paid status"""
         # This is a mock setup, for the sole purpose of testing the system.
        if self.billDB[billNumber]
        


# Creating Tools
@tool
def fetchUserDetails() -> str:
    """
    Function contains the information about the user. Returns information such as user name, account holder status, amazon id.
    """
    userDetails = '''User Name: Asutosh Dalei, Account Status: Active, Amazon ID: 12345'''
    userDetails = {'user_name':"Asutosh Dalei", "account_status":"Active", "amazon_id": 12345}

    return json.dumps(userDetails)

@tool
def fetchServiceList() -> str:
    """
    Function contains information of all available services using this platform.
    """
    serviceList = {'electricity':"Pay electricity bill", 'gas':"Pay the gas bill", 'water':"Pay the water bill", 'wifi':"pay the wifi bill"}
    return json.dumps(serviceList)

@tool
def payElectricityBill():
    """
    Function to deal with electricity bill related payments.
    """
    pass

tools = [fetchUserDetails, fetchServiceList]
toolsMap = {'fetchUserDetails':fetchUserDetails, "fetchServiceList":fetchServiceList}

llm = llm.bind_tools(tools)

# Central session messages
messages = [SystemMessage(content = "You are a helpful bill payment assistant for a user. Start by greeting the user.")]
global messages
aiMsg = llm.invoke(messages)
messages.append(aiMsg)

while True:
    if aiMsg.tool_calls:
        for toolCall in aiMsg.tool_calls:
            toolSelected = toolsMap[toolCall['name']]
            toolMsg = toolSelected.invoke(toolCall)
            messages.append(toolMsg)
        aiMsg = llm.invoke(messages)
        messages.append(aiMsg)
        print(f"AI Response:\n--> {aiMsg.content}")
        continue

    userInput = input("User Input:\n -->")
    if userInput == '/end':
        break
    if userInput == '/clear':
        messages = [SystemMessage(content = "You are a helpful bill payment assistant for a user. Start by greeting the user.")]
        aiMsg = llm.invoke(messages)
        messages.append(aiMsg)
        continue

    messages.append(HumanMessage(content=userInput))
    aiMsg = llm.invoke(messages)
    if aiMsg.content != '':
        print(f"AI Response:\n--> {aiMsg.content}")
    messages.append(aiMsg)

    # print(messages)