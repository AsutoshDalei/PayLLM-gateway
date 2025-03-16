# 🏦 Voice-Based Bill Payment System

## 🚀 Introduction

PayLLM is a conversational application that simplifies utility bill payments (electricity, gas, wifi, etc.) through natural language interactions. It enables users to manage their bills and make payments effortlessly by chatting with the system.

## ✨ Key Features

- **Conversational Bill Payments**: PayLLM lets users pay their utility bills via simple conversations, eliminating the need for complex interfaces.
- **Powered by LLaMa 3.2**: Utilizes the LLaMa 3.2 language model for accurate, intuitive understanding of user requests.
- **Agentic Framework**: Built with LangChain/LangGraph to call external tools, fetching service provider details, bills, and processing payments when needed.
- **Automated Task Handling**: Automatically retrieves and processes billing information and payments through integrated APIs.

## How It Works

1. **User Interaction**: Users ask PayLLM to fetch or pay bills, e.g., "Show my electricity bill."
2. **Task Execution**: The agentic framework identifies the task, invokes the necessary tools, and gathers required data.
3. **Payment Processing**: After confirmation, PayLLM processes the payment seamlessly.

## Technologies

- **Python**: The core programming language used for logic and integrations.
- **LLaMa 3.2**: The language model for conversational AI.
- **LangChain/LangGraph**: The agentic framework managing task orchestration and external tool calls.

PayLLM makes utility bill management easy and efficient with conversational AI and automated processes.

## 🛠️ Installation Guide

### 🔹 Step 1: Install Ollama
1️⃣ Download **Ollama** from the official website: [Ollama Download](https://ollama.com/download/windows)  
2️⃣ Install Ollama on your system.  
3️⃣ Open Command Prompt and run the following command to install **Llama3.2**:  
   ```sh
   ollama run llama3.2
   ```
4️⃣ To exit the Ollama prompt, use:  
   ```sh
   /bye
   ```
5️⃣ To restart Ollama anytime, run:  
   ```sh
   ollama run llama3.2
   ```

### 🔹 Step 2: Install Python & Dependencies
1️⃣ Download and install **Python 3.11.10** from [Python Official Website](https://www.python.org/downloads/).  
2️⃣ Set Python in your **environment variables**.  
3️⃣ Install the required dependencies by running:  
   ```sh
   pip3 install langchain
   pip3 install langchain_ollama
   pip3 install pyttsx3
   pip3 install SpeechRecognition
   pip3 install speech_recognition
   ```

### 🔹 Step 3: Clone the Project Repository
Clone this repository to your local machine:
```sh
git clone <your-repo-link>
cd voice-based-bill-payment-system
```

### 🔹 Step 4: Run the Application
Navigate to the project base directory and start the service by running:
```sh
python serviceClassLLM.py
```
📝 **Note:** `serviceClassLLM.py` is the main application that processes bill payments via voice interaction.

---

## 🎤 Usage Instructions
1️⃣ Run the app as mentioned above.  
2️⃣ Follow the voice prompts to provide bill details.  
3️⃣ Confirm payment when prompted.  
4️⃣ The AI will fetch, display, and process your bill payment securely.  

---
