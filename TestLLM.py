import base64
import hashlib
import json
import requests
import speech_recognition as sr
import pyttsx3
import datetime
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent

from langchain_core.prompts import ChatPromptTemplate

# Define the prompt
# Define a powerful prompt for Llama 3.2 to understand user intent
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are PayLLM, a smart bill payment assistant. Your job is to:\n"
               "1. Understand the user's intent (bill category, biller name, consumer ID, etc.).\n"
               "2. Ignore case differences (e.g., 'electricity' should match 'Electricity').\n"
               "3. Handle spelling mistakes and find the closest match.\n"
               "4. If the user input is unclear, ask them to clarify.\n"
               "5. Always respond with only the most relevant extracted value.\n"),
    ("human", "User said: {input}\n"
              "Available options: {options}\n"
              "Which option best matches the user input?"),
    ("placeholder", "{agent_scratchpad}")
])

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Initialize Speech Recognizer
recognizer = sr.Recognizer()

# API Configuration
API_BASE_URL = "http://localhost:8080/api/v2"
CLIENT_ID = "08ea8e5ce4a14e8096b0d758c2583c82"
AGENT_ID = "BL01BL02MBBA00000001"
HEADERS = {"Content-Type": "application/json"}


def get_best_match(user_input, options):
    """
    Uses Llama 3.2 to intelligently match user input to the best available option.
    This can be used for categories, billers, or any other type of selection.
    """
    response = llm.invoke({
        "input": user_input,
        "options": options
    })

    best_match = response.content.strip()

    # If the returned match is valid, use it
    if best_match.lower() in [opt.lower() for opt in options]:
        return best_match
    else:
        return None

# Function to Speak Text
def speak(text):
    engine.say(text)
    engine.runAndWait()


# Function to Get Voice Input
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"User: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't understand.")
            return ""
        except sr.RequestError:
            print("Speech recognition service unavailable.")
            return ""


# Function to Get Current Time Greeting
def get_greeting():
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 15:
        return "Good noon"
    elif 15 <= current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"


# Function to Generate a Sample Signature (Replace with actual logic)
def generate_signature(data):
    hash_object = hashlib.sha256(json.dumps(data).encode('utf-8'))
    signature = base64.b64encode(hash_object.digest()).decode('utf-8')
    return signature


# Tool: Fetch Category List from API
@tool
def fetch_category_list() -> str:
    """Fetch available bill categories from the API."""
    payload = {
        "client_id": CLIENT_ID,
        "data": {"agent_id": AGENT_ID},
        "reference_id": "AWPNSPVBPVPWDALTOMJSNBFQNOS41872263",
        "signature": generate_signature({"agent_id": AGENT_ID}),  # ✅ Generate a valid signature
        "timestamp": "2024-07-05T09:09:07+00:00",
        "ver": "1.0"
    }

    response = requests.get(f"{API_BASE_URL}/category/list", json=payload, headers=HEADERS)
    if response.status_code == 200 and response.json()["status"] == "success":
        categories = [cat["category_name"] for cat in response.json().get("categories", [])]
        return json.dumps(categories)
    return "Failed to fetch category list."


# Tool: Fetch Billers by Category
@tool
def fetch_billers_by_category(category_name: str) -> str:
    """Fetch billers based on category name from the API."""
    payload = {
        "client_id": CLIENT_ID,
        "data": {"agent_id": AGENT_ID, "category_name": category_name},
        "reference_id": "AWPNSPVBPVPWDALTOMJSNBFQNOS41878722",
        "signature": generate_signature({"agent_id": AGENT_ID}),  # ✅ Generate a valid signature
        "timestamp": "2024-07-05T09:10:13+00:00",
        "ver": "1.0"
    }

    response = requests.get(f"{API_BASE_URL}/biller/list", json=payload, headers=HEADERS)
    if response.status_code == 200 and response.json()["status"] == "success":
        billers = response.json().get("billers", [])
        return json.dumps(billers)
    return "No billers found for this category."


# Tool: Fetch Biller Details by Biller ID
@tool
def fetch_biller_details(biller_id: str) -> str:
    """Fetch biller details based on biller ID from the API."""
    payload = {
        "client_id": CLIENT_ID,
        "data": {"agent_id": AGENT_ID, "biller_id": biller_id},
        "reference_id": "BL01SPVBPVPWDALTOMJRNBFQNOS41878925",
        "signature": generate_signature({"agent_id": AGENT_ID}),  # ✅ Generate a valid signature
        "timestamp": "2024-07-05T09:13:09+00:00",
        "ver": "1.0"
    }

    response = requests.get(f"{API_BASE_URL}/biller/details", json=payload, headers=HEADERS)
    if response.status_code == 200 and response.json()["status"] == "success":
        return json.dumps(response.json()["biller"])
    return "Biller details not found."


# Initialize LangChain LLM with Tool Calling
llm = ChatOllama(model="llama3.2", temperature=0)
tools = [fetch_category_list, fetch_billers_by_category, fetch_biller_details]
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)


# Main Function
def event():
    greeting = get_greeting()
    print(f"{greeting}! Welcome to PayLLM.")
    speak(f"{greeting}! Welcome to PayLLM.")

    # Ask for Language Selection
    print("Please choose your language: English or Hindi?")
    speak("Please choose your language: English or Hindi?")
    language = listen()

    if language not in ["english", "hindi"]:
        print("Language not supported. Defaulting to English.")
        language = "english"

    # Fetch categories from API
    categories = json.loads(fetch_category_list.invoke({}))
    print(f"Available categories: {', '.join(categories)}")
    #speak(f"Available categories: {', '.join(categories)}")

    print("Which category do you want to pay a bill for?")
    speak("Which category do you want to pay a bill for?")
    category_name = listen()

    if category_name not in categories:
        print(f"❌ The category '{category_name}' is not supported.")
        speak(f"❌ The category '{category_name}' is not supported.")
        return

    # Fetch billers for selected category
    billers = json.loads(fetch_billers_by_category(category_name))
    biller_names = [b["biller_name"] for b in billers]

    print(f"Available billers for {category_name}: {', '.join(biller_names)}")
    speak(f"Available billers for {category_name}: {', '.join(biller_names)}")

    print("Which biller do you want to proceed with?")
    speak("Which biller do you want to proceed with?")
    biller_name = listen()

    # Find biller ID for the selected biller
    biller_id = None
    for b in billers:
        if b["biller_name"].lower() == biller_name.lower():
            biller_id = b["biller_id"]
            break

    if not biller_id:
        print("❌ Biller not found.")
        speak("❌ Biller not found.")
        return

    # Fetch biller details
    biller_details = json.loads(fetch_biller_details(biller_id))
    print(f"🔹 Biller Details: {json.dumps(biller_details, indent=4)}")
    speak(f"You have selected {biller_name}. Fetching details...")


try:
    event()
except Exception as e:
    print("Error:", e)
    speak("An error occurred. Please try again.")
