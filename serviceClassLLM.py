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
1. Ask the user the bill number.
2. Ask the user if you should fetch the bill details.
3. Inform the user the bill details once fetched.
4. Ask the user if you should pay the bill.
5. Is the user agrees, pay the bill.

You should never use external knowledge, assumptions or information beyond what is explicitly shared or recieved.
Strictly do not call tools unless absolutely needed.

Example:
User: Hello
PayLLM: Hi. To help with your payments, please provide your bill number.
User: 12345.
PayLLM: Sure, should I fetch the bill?
User: Yes, sure.
PayLLM: The bill amount is 145
User: Okay. Go ahead and pay it.
PayLLM: Sure.
PayLLM: The bill is paid.
'''

# initialSystemMessage = "Your name is asutosh"

class BillPay():
    def __init__(self, service: str, llm, billDB: dict):
        self.serviceTools = [self.fetchBill, self.payBill, self.eventSuccess]
        self.serviceTools = [self.fetchBill, self.payBill]
        # self.serviceTools = [self.fetchBill]
        # self.serviceTools = [self.fetchBill, self.eventSuccess]
        self.serviceToolsMap = {"fetchBill":self.fetchBill, "payBill": self.payBill, "eventSuccess": self.eventSuccess}
        self.service = service
        self.firstInteraction = True

        # self.llmService = llm.bind_tools(self.serviceTools)
        self.llmService = llm

        self.billDB = billDB

    @tool
    def fetchBill(self, billNumber):
        """
        Function to fetch bill details using bill number. Input: Bill Number. Output: Bill Amount, Bill Details
        Args:
            billNumber: Bill Number
        """
        # This is a mock setup, for the sole purpose of testing the system.
        try:
            return json.dumps(self.billDB[billNumber])
        except:
            return "Bill not found"
    
    @tool
    def payBill(self, billNumber: str) -> str:
        """Function to pay bill using bill number.
        Args:
            billNumber: Bill Number (String). Output: Bill paid status
        """
        print(billNumber, type(billNumber))
        if self.billDB[billNumber]['status'] == 'Paid':
            return "Bill paid already"
        self.billDB[billNumber]['status'] = 'Paid'
        return "Bill paid successfully"

    @tool
    def eventSuccess(self):
        """Function to define if event is successful or not. Unless you feel the event is successful, do not call this tool. Make sure the user is satisfied with the transaction."""
        return "eventSuccessFlag"
    
    def event(self):
        # serviceMessages = [SystemMessage(content = "You are a helpful bill payment assistant for a user. Restrict your response to just this task, nothing else. Strictly start by asking the user about the bill number. Do not start without the bill number. Followed by asking if you should fetch the bill or not. Followed by asking if you shoud pay the bill or not.")]
        # serviceMessages = [SystemMessage(content = "You are a helpful bill payment assistant for a user. Ask the user which bill number to pay? Do not execute functions without command.")]
        serviceMessages = [SystemMessage(content = initialSystemMessage), HumanMessage(content='Help me pay my bill. Ask me my bill number.')]
        
        eventFlag = "eventInProgress"

        aiMsgSer = self.llmService.invoke(serviceMessages)

        while eventFlag != 'eventSuccessFlag':
            if self.firstInteraction:
                print(f"AI Response:\n --> {aiMsgSer.content}")
                self.firstInteraction = False
                self.llmService = llm.bind_tools(self.serviceTools)

            if aiMsgSer.tool_calls:
                for toolCallSer in aiMsgSer.tool_calls:
                    print(toolCallSer)
                    print(toolCallSer["args"])
                    print(toolCallSer["args"].get("billNumber"))
                    toolSelected = self.serviceToolsMap[toolCallSer['name']]
                    if toolCallSer == 'eventSuccess':
                        eventFlag = toolSelected.invoke(toolCallSer)
                        break
                    toolMsg = toolSelected.invoke(toolCallSer["args"])
                    # toolMsg = toolSelected.invoke(toolCallSer["args"].get("billNumber"))
                    print(toolMsg)
                    serviceMessages.append(toolMsg)


                aiMsgSer = self.llmService.invoke(serviceMessages)
                serviceMessages.append(aiMsgSer)
                print(f"AI Response:\n --> {aiMsgSer.content}")
                continue
            userInput = input("User Input:\n -->")
            if userInput == "/end":
                break
            serviceMessages.append(HumanMessage(content = userInput))
            aiMsgSer = self.llmService.invoke(serviceMessages)
            if aiMsgSer.content != '':
                print(f"AI Response:\n--> {aiMsgSer.content}")
            serviceMessages.append(HumanMessage(content = userInput))

            
mockElectricityBills = {
    "9182":{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':32,'Amount':341, "Due Date":'10/01/2025', 'status':'Paid'},
    "1928":{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':37,'Amount':547, "Due Date":'11/02/2025','status':'Unpaid'},
    "1038":{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':23,'Amount':298, "Due Date":'09/10/2025','status':'Paid'}
}
mockElectricityBills = {
    9182:{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':32,'Amount':341, "Due Date":'10/01/2025', 'status':'Paid'},
    1928:{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':37,'Amount':547, "Due Date":'11/02/2025','status':'Unpaid'},
    1038:{'Customer Name':'Asutosh Dalei','service provider':'TS Elec Board','unit':23,'Amount':298, "Due Date":'09/10/2025','status':'Paid'}
}

mockWifiBills = {
    "8321":{'Customer Name':'Asutosh Dalei','service provider':'Airtel','Amount':1008, "Due Date":'04/03/2025', 'status':'Paid'},
    "1928":{'Customer Name':'Asutosh Dalei','service provider':'Airtel','Amount':1276, "Due Date":'04/02/2025','status':'Paid'},
    "1038":{'Customer Name':'Asutosh Dalei','service provider':'Airtel','Amount':1932, "Due Date":'08/04/2025','status':'Unpaid'}
}


elecBillPay = BillPay(service='Electricity', llm = llm, billDB=mockElectricityBills)
wifiBillPay = BillPay(service='WiFi', llm=llm, billDB=mockWifiBills)

try:
    elecBillPay.event()
except Exception as e:
    print(f"Error: {e}")
