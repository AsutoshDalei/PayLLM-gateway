import json
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph



import traceback

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


# Initialize the LLaMA 3.2 model
llm = ChatOllama(model="llama3.2:latest", temperature=0)
llm = ChatOllama(model="llama3.1:8b", temperature=0)

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
    """Funtion to get the list of providers based on user's state and bill service."""
    if state == '' or service == '':
        return f"Ask the user for the state and service."
    
    provList = serviceDB[state.lower()][service.lower()]
    print("HERE")

    return f"The service providers for {state} are: {provList}. Tell the entire list."

# Define tool to fetch bill details
@tool
def fetch_bill_details(state: str, provider: str, bill_number: str)->str:
    """Function to get the bill details based on state, provider, and bill number."""
    # Simulated API response with static data for now
    return f"The bill amount for {provider} in {state} (Bill No: {bill_number}) is ₹145."

# Define tool to process payment
@tool
def process_payment(bill_number: str)->str:
    """Function to processes payment for the given bill number."""
    return f"Payment for Bill No: {bill_number} has been successfully processed."

# @tool
# def general_purpose(query: str)->str:
#     """For general purpose user queries."""
#     return llm.invoke(HumanMessage(content = query))


initialSystemMessage = '''You are PayLLM, a conversational payment assistant. STRICTLY CALL TOOLS ONLY WHEN NEEDED.
Follow this structured flow. DO NOT DEVIATE, DO NOT ASSUME ANYTHING AND DO NOT HALLUCINATE:
1. Greet the user if they greet you.
2. Ask for the user's state, followed by the service.
3. Ask the user for the bill number.
4. Display the bill amount.
5. Ask for payment confirmation.
6. Confirm payment.
Maintain the flow based on previous responses.'''

# initialSystemMessage = '''You are PayLLM, a helpful assistant. Greet the user if the user greets you.'''

prompt_template = ChatPromptTemplate.from_messages(
    [   
        SystemMessage(content = initialSystemMessage),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

workflow = StateGraph(state_schema=MessagesState)

tools = [fetch_bill_details, process_payment, fetch_service_provider]
llmT = llm.bind_tools(tools)

def call_model(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = llmT.invoke(prompt)
    print(response)
    return {"messages": response}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "asutosh"}}

while True:
    query = input("User Input:\n --> ")
    if query.lower() == '/end': 
            break
    input_messages = [HumanMessage(query)]
    output = app.invoke({"messages": input_messages}, config)

    print(output["messages"][-1].content)
    # break