import json
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from langchain.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.agents import initialize_agent




import traceback

# Initialize the LLaMA 3.2 model
llm = ChatOllama(model="llama3.2:latest", temperature=0)

serviceDB = {'odisha':
        {
          'electricity':['OELE1', 'OELE2', 'OELE3'], 'gas':['OGAS1', 'OGAS2', 'OGAS3', 'OGAS4'], 'water':['OWAT1', 'OWAT2']
        },
    'goa':
        {
          'electricity':['GOELE1', 'GOELE2', 'GOELE2'], 'gas':['GOGAS1', 'GOGAS2', 'GOGAS3']
        },
    'telangana':
        {
          'electricity':['TSELE1', 'TSELE2', 'TSELE2', 'TSELE3'], 'gas':['TSGAS1', 'TSGAS2', 'TSGAS3']
        }
       }

# Define tool to fetch list of service providers
@tool
def fetch_service_provider(state: str, service: str)->str:
    """Fetches the list of providers based on user's state and bill service."""
    if state == '' or service == '':
        return f"Ask the user for the state and service."
    
    provList = serviceDB[state.lower()][service.lower()]
    print("HERE")

    return f"The service providers for {state} are: {provList}. Tell the entire list."

# Define tool to fetch bill details
@tool
def fetch_bill_details(state: str, provider: str, bill_number: str)->str:
    """Fetches bill details based on state, provider, and bill number."""
    # Simulated API response with static data for now
    return f"The bill amount for {provider} in {state} (Bill No: {bill_number}) is ₹145."

# Define tool to process payment
@tool
def process_payment(bill_number: str)->str:
    """Processes payment for the given bill number."""
    return f"Payment for Bill No: {bill_number} has been successfully processed."

@tool
def general_purpose(query: str)->str:
    """For general purpose user queries."""
    return llm.invoke(HumanMessage(content = query))


initialSystemMessage = '''You are PayLLM, a conversational payment assistant. Do not call tools unless absolutely needed.
Follow this structured flow:
1. Greet the user if they greet you.
2. Ask for the user's state, followed by the service provider and the bill number.
4. Fetching the bill by calling the fetch_bill_details tool.
6. Display the bill amount.
7. Ask for payment confirmation.
8. Confirm payment.
Maintain the flow based on previous responses.'''

# initialSystemMessage = '''You are PayLLM, a conversational payment assistant. You only speak in hinglish. DO NOT CALL ANY TOOLS. STRICTLY.'''

# globalMessages = [SystemMessage(content = initialSystemMessage), HumanMessage(content='Hello. Start my payment process.')]

# tools = [fetch_bill_details, process_payment, fetch_service_provider, general_purpose]
# toolsMap = {"fetch_bill_details":fetch_bill_details, "process_payment": process_payment, "fetch_service_provider":fetch_service_provider, 'general_purpose':general_purpose}
# llmService = llm.bind_tools(tools)

# aiMsgSer = llmService.invoke(globalMessages)
# while True:
#     print(globalMessages)
#     if aiMsgSer.tool_calls:
#         for toolCallSer in aiMsgSer.tool_calls:
#             print(f"TOOL:{toolCallSer['name']}")

#     userInput = input("User Input:\n -->")
#     if userInput == '/end':
#         break
#     globalMessages.append(HumanMessage(content = userInput))
#     aiMsgSer = llmService.invoke(globalMessages)
#     if aiMsgSer.content != '':
#         print(f"AI Response:\n--> {aiMsgSer.content}")
#     globalMessages.append(aiMsgSer)


memory = InMemoryChatMessageHistory(session_id="payment-session")

prompt = ChatPromptTemplate.from_messages([
    ("system", initialSystemMessage), 
    ("placeholder", "{chat_history}"),
    ("human", "{input}"), 
    ("placeholder", "{agent_scratchpad}"),
])

tools = [fetch_bill_details, process_payment, fetch_service_provider]
agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


while True:
    userInput = input("User Input:\n -->")
    if userInput == '/end':
        break
    resp = agent_executor.invoke({'input':userInput})
    print(resp['output'])