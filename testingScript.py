import json
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

import traceback

# Initialize the LLaMA 3.2 model
model = ChatOllama(model="llama3.2:latest", temperature=0)
