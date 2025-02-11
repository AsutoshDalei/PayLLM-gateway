# Importing necessary packages
import json

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Importing model
llm = ChatOllama(model="llama3.2", temperature=0)

class BillPay():
    def __init__(self, service: str, llm, billDB: dict):
        self.serviceTools = [self.fetchBill, self.payBill, self.eventSuccess]
        self.serviceToolsMap = {"fetchBill":self.fetchBill, "payBill": self.payBill, "eventSuccess": self.eventSuccess}
        self.service = service
        self.llmService = llm.bind_tools(self.serviceTools)

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
        """Function to define if event is successful or not. Unless you feel the event is successful, do not call this tool. Make sure the user is satisfied with the transaction."""
        return "eventSuccessFlag"
    
    def event(self):
        serviceMessages = [SystemMessage(content = "You are a helpful bill payment assistant for a user. Restrict your response to just this task, nothing else. Strictly start by asking the user about the bill number. Do not start without the bill number. Followed by asking if you should fetch the bill or not. Followed by asking if you shoud pay the bill or not.")]
        serviceMessages = [SystemMessage(content = "You are a helpful bill payment assistant for a user. Restrict your response to just this task, nothing else. Ask the user about the bill number first.")]
        
        eventFlag = "eventInProgress"

        aiMsgSer = self.llmService.invoke(serviceMessages)

        while eventFlag != 'eventSuccessFlag':
            if aiMsgSer.tool_calls:
                for toolCallSer in aiMsgSer.tool_calls:
                    toolSelected = self.serviceToolsMap[toolCallSer]
                    if toolCallSer == 'eventSuccess':
                        eventFlag = toolSelected.invoke(toolCallSer)
                        break
                    print(toolCallSer) 
                    
                    toolMsg = toolSelected.invoke(toolCallSer)
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
