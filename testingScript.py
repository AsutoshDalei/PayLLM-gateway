from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

import traceback

# Initialize the LLaMA 3.2 model
model = ChatOllama(model="llama3.2:latest", temperature=0)

memory = MemorySaver()
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are PayLLM, a conversational payment assistant.")
])

# agent_executor = create_react_agent(model, checkpointer=memory, prompt=prompt)
agent_executor = create_react_agent(model, checkpointer=memory)
config = {"configurable": {"thread_id": "def234"}}

try:
    while True:
        user_input = input("User Input:\n --> ")
        
        if user_input.lower() == '/end':  # End the conversation if the user types '/end'
            break
        
        # Invoke the agent to handle the conversation and return the response
        response = agent_executor.invoke({"input": user_input}, config)["output"]
except Exception as e:
    print("ERR", e)
