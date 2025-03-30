# Importing necessary packages
import json
import datetime

import speech_recognition as sr  # For voice input
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from num2words import num2words  # For date-to-words conversion

import torch
from parler_tts import ParlerTTSForConditionalGeneration  # For text-to-speech
from transformers import AutoTokenizer
import soundfile as sf
import sounddevice as sd

# Initialize Text-to-Speech Engine
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = ParlerTTSForConditionalGeneration.from_pretrained("ai4bharat/indic-parler-tts").to(device)
tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)

# Initialize Speech Recognizer
recognizer = sr.Recognizer()

# Importing model
llm = ChatOllama(model="llama3.2:latest", temperature=0)

# Enhanced System Prompt (inspired by first version’s clarity, tailored to second version’s flow)
initialSystemMessage = """
You are PayLLM, a friendly and natural-speaking virtual assistant designed to help users pay their bills easily.

### General Rules:
- In the first user interaction, respond **directly** with a welcoming message and ask if they want to pay a bill, without calling tools.
- Always **follow the structured step-by-step process** below, asking **one question at a time**.
- **Never assume information** or use external knowledge beyond what the user provides.
- Be conversational, polite, and clear in your responses. Avoid hallucination.

### Step-by-Step Process:
0. Greet the user and ask: "Would you like to pay a bill today?"
1. Ask: "Which state in India are you from?"
2. Ask: "What type of service is your bill for? For example, electricity, gas, or water."
3. After getting the service, use `fetch_service_provider` to list providers, then ask: "Which service provider is yours?"
4. Ask: "What’s your bill number?"
5. Confirm: "Should I fetch the details for your bill?"
6. After fetching, inform the user of the bill amount, due date, and status in a conversational sentence (e.g., "Your bill is X rupees, due on Y, and it’s currently Z.").
7. Ask: "Would you like me to pay this bill for you?"
8. If they agree, pay the bill and confirm: "Your bill has been paid successfully!"

### Notes:
- Only call tools after collecting all required info (state, service, provider, bill number).
- If the user says something unclear, politely ask them to repeat or clarify (e.g., "Sorry, I didn’t catch that. Could you tell me again?").
"""

# Databases (from second version, enriched with due date and status like the first)
serviceDB = {
    'odisha': {
        'electricity': ['OELE1', 'OELE2', 'OELE3'],
        'gas': ['OGAS1', 'OGAS2', 'OGAS3', 'OGAS4'],
        'water': ['OWAT1', 'OWAT2']
    },
    'telangana': {
        'electricity': ['TSELE1', 'TSELE2', 'TSELE3', 'TSELE4'],
        'gas': ['TSGAS1', 'TSGAS2', 'TSGAS3']
    }
}

billDB = {
    "ogas1": {
        "123a4": {"amount": "145 rupees", "due_date": "10/04/2025", "status": "Unpaid"},
        "135a7": {"amount": "512 rupees", "due_date": "15/04/2025", "status": "Unpaid"}
    },
    "ogas2": {
        "114b0": {"amount": "415 rupees", "due_date": "12/04/2025", "status": "Unpaid"}
    },
    "tsgas2": {
        "200c1": {"amount": "678 rupees", "due_date": "10/04/2025", "status": "Unpaid"}
    },
    "tsele2": {
        "400r7": {"amount": "290 rupees", "due_date": "10/04/2025", "status": "Unpaid"}
    }
}

# Function to Speak Text (from first version)
def speak(prompt: str):
    """Convert text to speech using ParlerTTS."""
    description = "A female speaker delivers a slightly expressive and animated speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up."
    description_input_ids = description_tokenizer(description, return_tensors="pt").to(device)
    prompt_input_ids = tokenizer(prompt, return_tensors="pt").to(device)

    generation = model.generate(input_ids=description_input_ids.input_ids,
                                attention_mask=description_input_ids.attention_mask,
                                prompt_input_ids=prompt_input_ids.input_ids,
                                prompt_attention_mask=prompt_input_ids.attention_mask)
    audio_arr = generation.cpu().numpy().squeeze()
    sd.play(audio_arr, model.config.sampling_rate)
    sd.wait()

# Function to Get Voice Input (from first version, with retry limit)
def listen():
    """Capture voice input with a retry limit."""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        for _ in range(3):
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                print(f"User: {text}")
                return text
            except sr.UnknownValueError:
                print("Sorry, I didn’t understand.")
                speak("I didn’t catch that. Could you say it again?")
                print("Listening...")
            except sr.RequestError:
                print("Speech recognition service unavailable.")
                speak("There seems to be an issue with voice recognition. Please try again.")
    speak("I couldn’t understand you after a few tries. Please try again later.")
    return ""

# Function to Convert Date to Words (from first version)
def date_to_words(date_str):
    """Convert a date (DD/MM/YYYY) into words."""
    try:
        day, month, year = map(int, date_str.split('/'))
        day_word = num2words(day, ordinal=True)
        month_name = datetime.date(year, month, day).strftime("%B")
        year_word = num2words(year)
        return f"{day_word} {month_name} {year_word}"
    except Exception:
        return "unknown date"

# Function to Get Current Time Greeting (from first version)
def get_greeting():
    """Return a time-based greeting."""
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 15:
        return "Good noon"
    elif 15 <= current_hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

# Tools (adapted from second version, enriched with first version’s details)
@tool
def fetch_service_provider(state: str, service: str) -> str:
    """Fetch a list of service providers based on state and service."""
    if not state or not service:
        return "I need both your state and service type to find providers."
    state = state.strip().lower()
    service = service.strip().lower()
    if state not in serviceDB:
        return f"Sorry, I don’t have service providers for '{state}'. Please check the state name."
    if service not in serviceDB[state]:
        return f"Sorry, I don’t have '{service}' providers listed for '{state}'."
    providers = serviceDB[state][service]
    return f"Here are the service providers for '{service}' in '{state}': {', '.join(providers)}."

@tool
def fetch_bill_details(provider: str, bill_number: str) -> str:
    """Fetch bill details based on provider and bill number."""
    if not provider or not bill_number:
        return "I need both the service provider and bill number to fetch your bill."
    provider = provider.strip().lower()
    bill_number = bill_number.strip()
    if provider not in billDB:
        return f"Sorry, I don’t have records for provider '{provider}'."
    if bill_number not in billDB[provider]:
        return f"I couldn’t find bill number '{bill_number}' for '{provider}'. Please check it."
    bill = billDB[provider][bill_number]
    return f"Your bill from '{provider}' (Bill No: {bill_number}) is {bill['amount']}, due on {date_to_words(bill['due_date'])}, and it’s currently {bill['status']}."

@tool
def pay_bill(provider: str, bill_number: str) -> str:
    """Simulate paying a bill."""
    if not provider or not bill_number:
        return "I need the service provider and bill number to pay your bill."
    provider = provider.strip().lower()
    bill_number = bill_number.strip()
    if provider not in billDB or bill_number not in billDB[provider]:
        return "I couldn’t find that bill. Please check the provider and bill number."
    if billDB[provider][bill_number]["status"] == "Paid":
        return "This bill is already paid!"
    billDB[provider][bill_number]["status"] = "Paid"
    return f"Your bill from '{provider}' (Bill No: {bill_number}) has been paid successfully!"

# Main Event Loop
def event(llm):
    memory = [SystemMessage(content=initialSystemMessage)]
    tools = [fetch_service_provider, fetch_bill_details, pay_bill]
    toolsMap = {"fetch_service_provider": fetch_service_provider, "fetch_bill_details": fetch_bill_details, "pay_bill": pay_bill}
    llmService = llm.bind_tools(tools)

    # Initial greeting
    welcome_message = f"{get_greeting()}! I’m PayLLM, here to help you pay your bills easily. Would you like to pay a bill today?"
    speak(welcome_message)
    memory.append(AIMessage(content=welcome_message))
    print(f"AI Response:\n --> {welcome_message}")

    while True:
        userInput = listen()
        if userInput.lower() in ["/end", "exit", "quit", "stop"]:
            speak("Goodbye! Have a great day!")
            break

        memory.append(HumanMessage(content=userInput))
        aiMsg = llmService.invoke(memory)

        if aiMsg.tool_calls:
            for toolCall in aiMsg.tool_calls:
                if toolCall['name'] in toolsMap:
                    toolMsg = toolsMap[toolCall['name']].invoke(toolCall)
                    memory.append(ToolMessage(content=toolMsg, tool_call_id=toolCall['id']))
            aiMsg = llmService.invoke(memory)

        memory.append(aiMsg)
        print(f"AI Response:\n --> {aiMsg.content}")
        speak(aiMsg.content)

# Main Loop with Error Handling
while True:
    try:
        event(llm)
    except Exception as e:
        print(f"ERR: {e}")
        speak("Oops, something went wrong. Let’s try again. Would you like to pay a bill?")
        continue