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
    def __init__(self, service: str, llm, billDB: dict):
        serviceTools = [self.fetchBill, self.payBill]
        self.service = service
        self.llmService = llm.bind_tools(serviceTools)

        # self.userDetails = fetchUserDetails()
        self.billDB = billDB

    @tool
    def fetchBill(self, billNumber):
        """Function to fetch bill details using bill number. Input: Bill Number. Output: Bill Amount, Bill Details"""
        # This is a mock setup, for the sole purpose of testing the system.
        try:
            return json.dumps(self.billDB[billNumber])
        except:
            return "Bill not found"
    
    @tool
    def payBill(self, billNumber):
        """Function to pay bill using bill number. Input: Bill Number. Output: Bill paid status"""
         # This is a mock setup, for the sole purpose of testing the system.
        if self.billDB[billNumber]['status'] == 'Paid':
            return "Bill paid already"
        self.billDB[billNumber]['status'] = 'Paid'
        return "Bill paid successfully"

    @tool
    def eventSuccess(self):
        """Function to define if event is successful or not. Unless you feel the event is successful, do not call this tool."""
        return "eventSuccessFlag"
    
    def event(self):
        serviceMessages = [SystemMessage(content = "You are a helpful bill payment assistant for a user. Restrict your response to just this task, nothing else. Strictly start by asking the user about the bill number. Followed by asking if you should fetch the bill or not. Followed by asking if you shoud pay the bill or not.")]
        



        
elecBillPay = BillPay(service='Electricity', llm = llm, billDB=mockElectricityBills)
wifiBillPay = BillPay(service='WiFi', llm=llm, billDB=mockWifiBills)

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
    Tool to handle all electricity bill related payments.
    """
    print("entered here")
    elecBillPay.event()

tools = [fetchUserDetails, fetchServiceList, payElectricityBill]
toolsMap = {'fetchUserDetails':fetchUserDetails, "fetchServiceList":fetchServiceList, "payElectricityBill":payElectricityBill}

llm = llm.bind_tools(tools)

# Central session messages
global messages
# messages = [SystemMessage(content = "You are a helpful bill payment assistant for a user. Start by greeting the user.")]
messages = [SystemMessage(content = "You are a helpful bill payment assistant for a user. Restrict your response to just this task, nothing else. Strictly start by asking the user about the bill number. Followed by asking if you should fetch the bill or not. Followed by asking if you shoud pay the bill or not.")]


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
        messages = [SystemMessage(content = "You are a helpful bill payment assistant for a user. Do not hallucinate. Restrict yourself to information that you know of for sure onlt. Start by greeting the user.")]
        aiMsg = llm.invoke(messages)
        messages.append(aiMsg)
        continue

    messages.append(HumanMessage(content=userInput))
    aiMsg = llm.invoke(messages)
    if aiMsg.content != '':
        print(f"AI Response:\n--> {aiMsg.content}")
    messages.append(aiMsg)

    # print(messages)