# Importing necessary packages
import json
import re

import datetime
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Importing model
llm = ChatOllama(model="llama3.2:latest", temperature=0)

LANGUAGE = 'english'
initialSystemMessage1 = '''You are VoxPay, a conversational payment assistant EXCLUSIVELY in India.
### General Rules:
- NEVER call tools or proceed to the next step until you have collected all required information from the user.
- Ask ONE question at a time, wait for the user’s response, and store it before moving forward.
- Output ONLY the response for the current step, nothing else.
- Do NOT repeat earlier messages or include examples unless explicitly asked.
- Follow this EXACT sequence:

### Step-by-Step Process:
1. Greet the user with: "I’m VoxPay, your personal bill payment assistance. I am here to help you with your bill payment. Kindly mention the language you want to converse in (English, Hindi, Telugu)."
2. After the user selects a language, say: "You have chosen [LANGUAGE]. To help with your bill payments, please provide your state in India where the bill is related."
3. After the state is provided, say: "please provide your utility category? Options are: electricity, water, or gas."
4. After the utility category is provided, say: "Please provide your service provider name."
5. After the service provider is provided, say: "Please provide your consumer number."
6. After the consumer number is provided, with the help of service provider name and consumer number, fetch the bill. say: "Thanks for providing the details. Hold on! I am fetching your bill details."
7. Display the consumer number, Customer Name, bill amount, due date, and service provider name in a single statement. say: "Do you want me to pay yor bill. If yes please enter your UIP pin"
8. Confirm payment. Say: Your bill payment has been successfully processed.

### Additional Rules:
- If the user provides incomplete or unclear input (e.g., misspelled state), ask for clarification instead of guessing.
- Do not mention utility service providers until the user specifies the utility category.
- Once bill paid you should remember only selected state name, incase your want to pay any other bill.
'''

#State database  for state validation
stateDB = {'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'}

utilityServiceDB = {'electricity', 'gas', 'water','mobile'}

# service provider Database based on states
serviceDB = {
    'andhra_pradesh': {
        'electricity': ['APEPDCL','APSPDCL'],
        'gas': ['IOCL','HPCL','BPCL'],
        'water': ['APWRD'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'assam': {
        'electricity': ['APDCL'],
        'gas': ['AGCL'],
        'water': ['APHE'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'bihar': {
        'electricity': ['NBPDCL','SBPDCL'],
        'gas': ['GAIL'],
        'water': ['BPHE'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'chhattisgarh': {
        'electricity': ['CSPDCL'],
        'gas': ['GAIL'],
        'water': ['CPHE'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'goa': {
        'electricity': ['GED'],
        'gas': ['IOCL','HPCL','BPCL'],
        'water': ['PWD'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'gujarat': {
        'electricity': ['DGVCL','MGVCL','PGVCL','UGVCL'],
        'gas': ['GGL'],
        'water': ['GWSSB'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'haryana': {
        'electricity': ['DHBVN','UHBVN'],
        'gas': ['HCGDL'],
        'water': ['PHED'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'himachal_pradesh': {
        'electricity': ['HPSEBL'],
        'gas': ['IOCL','HPCL','BPCL'],
        'water': ['IPH'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'jharkhand': {
        'electricity': ['JBVNL'],
        'gas': ['GAIL'],
        'water': ['JPHE'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'karnataka': {
        'electricity': ['BESCOM','MESCOM','HESCOM','GESCOM','CESCOM'],
        'gas': ['GAIL'],
        'water': ['BWSSB'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'kerala': {
        'electricity': ['KSEB'],
        'gas': ['IOAGPL'],
        'water': ['KWA'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'madhya_pradesh': {
        'electricity': ['MPPGCL','MPPTCL','MPPKVVCL','MPMKVVCL','MPPKVVCL'],
        'gas': ['GAIL'],
        'water': ['MPUDC'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'maharashtra': {
        'electricity': ['MSEDCL','TPC','AEML'],
        'gas': ['MGL'],
        'water': ['MMRDA'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'manipur': {
        'electricity': ['MSPDCL'],
        'gas': ['IOCL','HPCL','BPCL'],
        'water': ['PHED'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'meghalaya': {
        'electricity': ['MePDCL'],
        'gas': ['IOCL','HPCL','BPCL'],
        'water': ['PHED'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'mizoram': {
        'electricity': ['P&E'],
        'gas': ['IOCL','HPCL','BPCL'],
        'water': ['PHED'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'nagaland': {
        'electricity': ['DoP'],
        'gas': ['IOCL','HPCL','BPCL'],
        'water': ['PHED'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'odisha': {
        'electricity': ['TPNODL','TPSODL','TPCODL','TPWODL'],
        'gas': ['GAIL'],
        'water': ['PHEO'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'punjab': {
        'electricity': ['PSPCL'],
        'gas': ['GAIL'],
        'water': ['PWSSB'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'rajasthan': {
        'electricity': ['JVVNL','AVVNL','JdVVNL'],
        'gas': ['RSGL'],
        'water': ['PHED'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'sikkim': {
        'electricity': ['Sikkim Power'],
        'gas': ['IOCL','HPCL','BPCL'],
        'water': ['PHED'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'tamil_nadu': {
        'electricity': ['TANGEDCO'],
        'gas': ['IOCL'],
        'water': ['CMWSSB'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    },
    'telangana': {
        'electricity': ['TSSPDCL','TSNPDCL'],
        'gas': ['BGL'],
        'water': ['HMWSSB'],
        'mobile': ['Airtel','BSNL','Jio','Vi']
    }
}

billDB = {
    # Andhra Pradesh
    2001: {'Customer Name': 'Ravi Teja', 'service provider': 'APSPDCL', 'unit': 42, 'Amount': 550,
           'Due Date': '15/04/2025', 'status': 'Paid', 'service': 'electricity'},
    2002: {'Customer Name': 'Divya Reddy', 'service provider': 'HPCL', 'Amount': 1050, 'Due Date': '18/07/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2003: {'Customer Name': 'Manoj Kumar', 'service provider': 'Vijayawada Water Board', 'Amount': 700,
           'Due Date': '10/11/2025', 'status': 'Paid', 'service': 'water'},
    2004: {'Customer Name': 'Sita Devi', 'service provider': 'Jio', 'Amount': 499, 'Due Date': '05/05/2026',
           'status': 'Unpaid', 'service': 'mobile'},

    # Arunachal Pradesh
    2005: {'Customer Name': 'Tenzing Norbu', 'service provider': 'Arunachal Power', 'unit': 30, 'Amount': 460,
           'Due Date': '20/06/2025', 'status': 'Paid', 'service': 'electricity'},
    2006: {'Customer Name': 'Karma Dorjee', 'service provider': 'IOCL', 'Amount': 980, 'Due Date': '12/08/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2007: {'Customer Name': 'Dorjee Wangchuk', 'service provider': 'AP Jal Board', 'Amount': 620,
           'Due Date': '07/10/2025', 'status': 'Paid', 'service': 'water'},
    2008: {'Customer Name': 'Sonam Bhutia', 'service provider': 'Airtel', 'Amount': 799, 'Due Date': '20/07/2026',
           'status': 'Unpaid', 'service': 'mobile'},

    # Assam
    2009: {'Customer Name': 'Debashish Das', 'service provider': 'APDCL', 'unit': 55, 'Amount': 730,
           'Due Date': '25/08/2025', 'status': 'Paid', 'service': 'electricity'},
    2010: {'Customer Name': 'Priyanka Bora', 'service provider': 'Bharat Gas', 'Amount': 1100, 'Due Date': '15/09/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2011: {'Customer Name': 'Anurag Deka', 'service provider': 'Guwahati Jal Board', 'Amount': 850,
           'Due Date': '12/12/2025', 'status': 'Paid', 'service': 'water'},
    2012: {'Customer Name': 'Rohit Mahanta', 'service provider': 'Vodafone Idea', 'Amount': 649,
           'Due Date': '30/06/2026', 'status': 'Unpaid', 'service': 'mobile'},

    # Bihar
    2013: {'Customer Name': 'Satyam Kumar', 'service provider': 'NBPDCL', 'unit': 48, 'Amount': 600,
           'Due Date': '10/09/2025', 'status': 'Paid', 'service': 'electricity'},
    2014: {'Customer Name': 'Nidhi Jha', 'service provider': 'GAIL', 'Amount': 1250, 'Due Date': '05/10/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2015: {'Customer Name': 'Alok Prasad', 'service provider': 'Patna Jal Parishad', 'Amount': 920,
           'Due Date': '20/11/2025', 'status': 'Paid', 'service': 'water'},
    2016: {'Customer Name': 'Neeraj Singh', 'service provider': 'BSNL', 'Amount': 549, 'Due Date': '05/07/2026',
           'status': 'Unpaid', 'service': 'mobile'},

    # Chhattisgarh
    2017: {'Customer Name': 'Vinod Tiwari', 'service provider': 'CSPDCL', 'unit': 52, 'Amount': 670,
           'Due Date': '15/10/2025', 'status': 'Paid', 'service': 'electricity'},
    2018: {'Customer Name': 'Megha Verma', 'service provider': 'Indane Gas', 'Amount': 1300, 'Due Date': '10/11/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2019: {'Customer Name': 'Kiran Das', 'service provider': 'Raipur Jal Board', 'Amount': 990,
           'Due Date': '25/12/2025', 'status': 'Paid', 'service': 'water'},
    2020: {'Customer Name': 'Arjun Sharma', 'service provider': 'MTNL', 'Amount': 599, 'Due Date': '10/08/2026',
           'status': 'Unpaid', 'service': 'mobile'},

    # Telangana
    2021: {'Customer Name': 'Arun Reddy', 'service provider': 'TSSPDCL', 'unit': 50, 'Amount': 620,
           'Due Date': '12/05/2025', 'status': 'Paid', 'service': 'electricity'},
    2022: {'Customer Name': 'Meena Rao', 'service provider': 'HPCL', 'Amount': 1150, 'Due Date': '15/08/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2023: {'Customer Name': 'Ramesh Goud', 'service provider': 'Hyderabad Water Board', 'Amount': 760,
           'Due Date': '18/10/2025', 'status': 'Paid', 'service': 'water'},
    2024: {'Customer Name': 'Priya Nair', 'service provider': 'Airtel', 'Amount': 699, 'Due Date': '25/07/2026',
           'status': 'Unpaid', 'service': 'mobile'},

    # Odisha
    2025: {'Customer Name': 'Deepak Mohanty', 'service provider': 'TPNODL', 'unit': 45, 'Amount': 590,
           'Due Date': '22/06/2025', 'status': 'Paid', 'service': 'electricity'},
    2026: {'Customer Name': 'Kavita Das', 'service provider': 'Bharat Gas', 'Amount': 1120, 'Due Date': '28/08/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2027: {'Customer Name': 'Sanjay Pattnaik', 'service provider': 'PHEO', 'Amount': 830,
           'Due Date': '30/12/2025', 'status': 'Paid', 'service': 'water'},
    2028: {'Customer Name': 'Sneha Mishra', 'service provider': 'Vodafone Idea', 'Amount': 649,
           'Due Date': '15/09/2026', 'status': 'Unpaid', 'service': 'mobile'},

    # West Bengal
    2029: {'Customer Name': 'Subhajit Roy', 'service provider': 'WBSEDCL', 'unit': 60, 'Amount': 780,
           'Due Date': '18/07/2025', 'status': 'Paid', 'service': 'electricity'},
    2030: {'Customer Name': 'Ankita Bose', 'service provider': 'Indane Gas', 'Amount': 1220, 'Due Date': '22/09/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2031: {'Customer Name': 'Amitava Sen', 'service provider': 'Kolkata Water Supply', 'Amount': 910,
           'Due Date': '27/11/2025', 'status': 'Paid', 'service': 'water'},
    2032: {'Customer Name': 'Debjani Ghosh', 'service provider': 'BSNL', 'Amount': 599, 'Due Date': '10/10/2026',
           'status': 'Unpaid', 'service': 'mobile'},

    # Tamil Nadu
    2033: {'Customer Name': 'Vikram Iyer', 'service provider': 'TANGEDCO', 'unit': 55, 'Amount': 750,
           'Due Date': '20/08/2025', 'status': 'Paid', 'service': 'electricity'},
    2034: {'Customer Name': 'Lakshmi Raman', 'service provider': 'HPCL', 'Amount': 1180, 'Due Date': '25/10/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2035: {'Customer Name': 'Rajeshwari M', 'service provider': 'Chennai Water Supply', 'Amount': 890,
           'Due Date': '05/12/2025', 'status': 'Paid', 'service': 'water'},
    2036: {'Customer Name': 'Suresh Kumar', 'service provider': 'Jio', 'Amount': 799, 'Due Date': '30/11/2026',
           'status': 'Unpaid', 'service': 'mobile'},

    # Karnataka
    2037: {'Customer Name': 'Rajesh Shetty', 'service provider': 'BESCOM', 'unit': 48, 'Amount': 710,
           'Due Date': '25/06/2025', 'status': 'Paid', 'service': 'electricity'},
    2038: {'Customer Name': 'Anjali Rao', 'service provider': 'Indane Gas', 'Amount': 1230, 'Due Date': '20/09/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2039: {'Customer Name': 'Vivek Patil', 'service provider': 'Bangalore Water Supply', 'Amount': 860,
           'Due Date': '15/11/2025', 'status': 'Paid', 'service': 'water'},
    2040: {'Customer Name': 'Sneha Kulkarni', 'service provider': 'Airtel', 'Amount': 599, 'Due Date': '05/10/2026',
           'status': 'Unpaid', 'service': 'mobile'},

    # Maharashtra
    2041: {'Customer Name': 'Amit Joshi', 'service provider': 'MSEB', 'unit': 52, 'Amount': 730, 'Due Date': '10/06/2025', 'status': 'Paid', 'service': 'electricity'},
    2042: {'Customer Name': 'Neha Deshmukh', 'service provider': 'Bharat Gas', 'Amount': 1190, 'Due Date': '18/09/2025', 'status': 'Unpaid', 'service': 'gas'},
    2043: {'Customer Name': 'Rohit Patil', 'service provider': 'Mumbai Water Board', 'Amount': 920, 'Due Date': '28/11/2025', 'status': 'Paid', 'service': 'water'},
    2044: {'Customer Name': 'Pooja Sharma', 'service provider': 'Vodafone Idea', 'Amount': 699, 'Due Date': '05/10/2026', 'status': 'Unpaid', 'service': 'mobile'},

    # Goa
    2045: {'Customer Name': 'Anil Naik', 'service provider': 'Goa Electricity Dept', 'unit': 48, 'Amount': 690,
           'Due Date': '15/05/2025', 'status': 'Paid', 'service': 'electricity'},
    2046: {'Customer Name': 'Sneha Gaonkar', 'service provider': 'HPCL', 'Amount': 1100, 'Due Date': '20/07/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2047: {'Customer Name': 'Rohan Kamat', 'service provider': 'Panjim Water Board', 'Amount': 850,
           'Due Date': '25/10/2025', 'status': 'Paid', 'service': 'water'},
    2048: {'Customer Name': 'Vishal Desai', 'service provider': 'Jio', 'Amount': 599, 'Due Date': '08/09/2026',
           'status': 'Unpaid', 'service': 'mobile'},

    # Uttar Pradesh
    2049: {'Customer Name': 'Arvind Mishra', 'service provider': 'UPPCL', 'unit': 58, 'Amount': 810,
           'Due Date': '12/06/2025', 'status': 'Paid', 'service': 'electricity'},
    2050: {'Customer Name': 'Pallavi Singh', 'service provider': 'Indane Gas', 'Amount': 1250, 'Due Date': '22/08/2025',
           'status': 'Unpaid', 'service': 'gas'},
    2051: {'Customer Name': 'Rajeev Yadav', 'service provider': 'Lucknow Jal Sansthan', 'Amount': 880,
           'Due Date': '30/12/2025', 'status': 'Paid', 'service': 'water'},
    2052: {'Customer Name': 'Nikita Verma', 'service provider': 'Airtel', 'Amount': 699, 'Due Date': '15/11/2026',
           'status': 'Unpaid', 'service': 'mobile'},

    # Delhi
    2053: {'Customer Name': 'Amit Sharma', 'service provider': 'BSES Rajdhani', 'unit': 62, 'Amount': 920, 'Due Date': '18/06/2025', 'status': 'Paid', 'service': 'electricity'},
    2054: {'Customer Name': 'Priya Mehta', 'service provider': 'Indane Gas', 'Amount': 1300, 'Due Date': '25/08/2025', 'status': 'Unpaid', 'service': 'gas'},
    2055: {'Customer Name': 'Suresh Gupta', 'service provider': 'Delhi Jal Board', 'Amount': 890, 'Due Date': '05/12/2025', 'status': 'Paid', 'service': 'water'},
    2056: {'Customer Name': 'Anjali Verma', 'service provider': 'Airtel', 'Amount': 799, 'Due Date': '20/11/2026', 'status': 'Unpaid', 'service': 'mobile'}

    # More states added here following the same format...
}

# This ensures the user isn't asked repeatedly for their language
@tool
def set_language(user_input: str):
    """
    Sets the user's language preference.
    Accepts 'English', 'Hindi', 'Telugu', 'odia', 'tamil', 'marathi', or 'bangali'.
    """
    valid_languages = ["english", "hindi", "telugu", "tamil", "marathi","odia","bangali"]

    if user_input.lower() in valid_languages:
        return f"Language set to {user_input}. Please provide the state in India where the bill is related."

    return "Invalid choice. Please select a language: English, Hindi, Telugu, Odia, Tamil, Marathi, or Bengali."

# This prevents issues like "Canada" being accepted.
@tool
def validate_state(user_input: str):
    """
    Validates if the user has provided a valid state in India.
    """
    user_input = user_input.title().strip()  # Normalize input

    if user_input in stateDB:
        return f"State set to {user_input}. Please select a utility type: Electricity, Water, or Gas."

    return "Currently, VoxPay supports bill payments only in India. Please enter a valid Indian state."

@tool
def validate_utility_category_type(utility_name: str):
    """
    Validates if the given service is supported by VoxPay.

    Args:
        utility_name (str): The utility service name provided by the user.
    """
    utility_name = utility_name.title().strip().lower()  # Normalize input

    if utility_name in utilityServiceDB:
        return f"You have chose {utility_name}. Please provide your service provider name."

    return f"Currently, VoxPay is not supporting {utility_name} category. Please enter another utility service name to proceed with."

# The system won’t assume "2025" is incorrect—it will ask for confirmation.
@tool
def validate_consumer_number(user_input: str):
    """
    Ensures the provided consumer number is valid.
    If the number looks like a year (e.g., 2025), asks for confirmation.
    """
    #if re.match(r"^(19|20)\d{2}$", user_input):
        #return f"It seems like you've entered {user_input}. Is this your actual consumer number? (yes/no)"

    return f"Consumer number {user_input} received. Fetching your bill details..."


@tool
def fetch_service_provider(service: str, state: str, provider: str) -> str:
    """
    Fetches a list of service providers based on the user's state and bill service.
    Also validates if a given service provider is valid for the state and service.

    Args:
        service (str): The type of service for which the user wants to pay the bill.
        state (str): The state of residence of the user.
        provider (str, optional): The service provider name to validate.
    Returns:
        str: str: A message containing either the list of service providers or a validation result.
    """

    if not state or not service:
        return "Please specify both the state and the service type to fetch providers."

    state = state.strip().lower()
    service = service.strip().lower()

    if state not in serviceDB:
        return f"Sorry, I couldn't find service providers for '{state}'. Please check the state name."

    if service not in serviceDB[state]:
        return f"Sorry, there are no listed providers for '{service}' in '{state}'."

    available_providers = serviceDB[state][service]

    if provider:
        provider = provider.strip()
        if provider in available_providers:
            return f"'{provider}' is a valid service provider for '{service}' in '{state}'."
        else:
            return f"'{provider}' is not a valid service provider for '{service}' in '{state}'. Available providers: {', '.join(available_providers)}."

    return f"The available service providers for '{service}' in '{state}' are: {', '.join(available_providers)}."


# Tool to fetch bill details based on consumer number
@tool
def fetch_bill_details(consumer_number: int, service_provider: str) -> str:
    """
    Fetches bill details based on consumer number and service provider name.
    Args:
        consumer_number (int): The user's consumer number.
        service_provider (str): The service provider name.
    Returns:
        str: A message containing the bill amount or an appropriate error message.
    """
    # Check if both provider and bill number are provided
    if not consumer_number or not service_provider:
        return "Please provide the consumer number and service provider name to fetch bill details."

    # Check if the consumer  number exists in the provider's record in billDB
    if consumer_number not in billDB:
        assert "BillNum Err"
        return f"Invalid consumer number '{consumer_number}'. Please double-check your bill number."

    # Fetch and return the bill amount
    bill_details = billDB[consumer_number]
    return f"The status of consumer number: {consumer_number} of {bill_details['service']} utility is {bill_details['status']} for rupees {bill_details['Amount']} due {bill_details['Due Date']}. To confirm, you would like to proceed with the payment? If yes, please enter your UPI pin to authenticate the payment request."

@tool
def process_bill_payment(service: str, provider: str, state: str, consumer_number: str, amount: float, upi_pin: str) -> str:
    """
    Processes the bill payment for the given utility service.

    Args:
        service (str): The utility service type (electricity, gas, water, mobile).
        provider (str): The service provider name.
        state (str): The state in India where the bill applies.
        consumer_number (str): The consumer ID or bill account number.
        amount (float): The bill amount.
        upi_pin (str): The UPI PIN for authentication.

    Returns:
        str: A message indicating whether the bill payment was successful or failed.
    """

    # Validate the service type
    if service.lower() not in utilityServiceDB:
        return f"'{service}' is not a valid utility service. Please choose from {', '.join(utilityServiceDB)}."

    # Validate required details
    if not (provider and state and consumer_number and amount and upi_pin):
        return "Missing required details. Please provide service, provider, state, consumer number, amount, and UPI PIN."

    # Simulate payment success/failure
    validation_sucess = True
    #payment_success = random.choice([True, False])

    if validation_sucess:
        return f"Bill payment of ₹{amount:.2f} for {service} with {provider} (Consumer No: {consumer_number}) in {state} was successful! Would you like to:  \nPay another bill (same service, different provider/consumer number) \nChoose a different utility type\n"
    else:
        return f"Bill payment failed. Please check your details and try again."

# This avoids forcing the user to restart the process after paying one bill.
@tool
def post_payment_navigation():
    """
    Provides options to the user after successful payment.
    """
    return "Payment successful! Would you like to: \n" \
           "1️. Pay another bill (same service, different provider/consumer number)\n" \
           "2️. Choose a different utility type\n" \
           "3️. Exit"

# Function to Get Current Time Greeting (from first version)
#@tool
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

tools = [set_language, validate_state, validate_utility_category_type, validate_consumer_number, fetch_service_provider, fetch_bill_details,process_bill_payment,
             post_payment_navigation]
toolsMap = {"set_language": set_language, "validate_state": validate_state, "validate_utility_category_type": validate_utility_category_type,
                "validate_consumer_number": validate_consumer_number, "fetch_service_provider": fetch_service_provider,
                "fetch_bill_details": fetch_bill_details,"process_bill_payment" : process_bill_payment, "post_payment_navigation": post_payment_navigation}
llmTool = llm.bind_tools(tools)


def event():
    LANGUAGE = input(
        f"{get_greeting()}! I’m VoxPay, your personal bill payment assistance. I am here to help you with your bill payment.\nKindly mention the language you want to converse in (English, Hindi, Telugu):\n -->")

    memory = [SystemMessage(content=initialSystemMessage1), HumanMessage(content=f"I've chosen {LANGUAGE}. Let's start my payment process.")]
    # memory = [SystemMessage(content = initialSystemMessage2)]

    #tools = [set_language,fetch_service_provider, fetch_bill_details]
   # toolsMap = {"fetch_service_provider": fetch_service_provider, "fetch_bill_details": fetch_bill_details}

    #llmService = llm
   # llmTool = llm.bind_tools(tools)

    firstInteraction = True

    while True:
        userInput = input("User Input:\n -->").lower()
        if userInput == '/end':
            break
        memory.append(HumanMessage(content=userInput))
        aiMsg = llmTool.invoke(memory)

        if aiMsg.tool_calls:
            for toolCall in aiMsg.tool_calls:
                if toolCall['name'] in toolsMap:
                    # print(f"TOOLCALL: {toolCall['name']}")
                    toolMsg = toolsMap[toolCall['name']].invoke(toolCall)
                    memory.append(toolMsg)
            aiMsg = llmTool.invoke(memory)
        print(f"AI Response:\n--> {aiMsg.content}\n")


try:
    event()
except Exception as e:
    print(f"ERR: {e}")

# script = ['Hello', "I live in Odisha", "I want to pay my gas bill", "My service provider is OGAS1 and my bill number is 123a4"]


