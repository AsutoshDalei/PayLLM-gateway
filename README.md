# PayLLM

PayLLM is a conversational application that simplifies utility bill payments (electricity, gas, wifi, etc.) through natural language interactions. It enables users to manage their bills and make payments effortlessly by chatting with the system.

## Key Features

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
