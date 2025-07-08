import os
from dotenv import load_dotenv
load_dotenv()
#from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
#from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema.output import ChatGeneration, Generation
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

# Load API key from .env
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=openai_api_key,
    model_kwargs={"response_format": "json"}
)

memory = ConversationBufferMemory(return_messages=True)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

user_state = {
    "step": "ask_name",
    "name": "",
    "goal": "",
    "insight_requested": False,
    "insight_text": "",
    "income": {},
    "expenses": {}
}

income_categories = ["Part-time job", "Scholarships", "Parental support", "Freelance gigs", "Others"]
expense_categories = ["Rent", "Groceries", "Tuition", "Transportation", "Emergency Fund", "Eating out", "Car Insurance", "Credit Card Payments", "Textbooks", "Utilities", "Others"]

def extract_number(text):
    import re
    match = re.search(r"\d+", text.replace(',', ''))
    return int(match.group()) if match else 0

def format_dict_as_bullet_list(title, data):
    lines = [f"{title}:"]
    for key, value in data.items():
        lines.append(f"• {key}: ${value}")
    return "\n".join(lines)

def run_chatbot(user_input: str) -> str:
    step = user_state["step"]

    if user_input.lower() in ["restart", "start over", "reset", "refresh"]:
        user_state.update({
            "step": "ask_name",
            "name": "",
            "goal": "",
            "insight_requested": False,
            "insight_text": "",
            "income": {},
            "expenses": {}
        })
        return "Let's start fresh.\nWhat's your name?"

    if step == "ask_name":
        user_state["name"] = user_input.strip().title()
        user_state["step"] = "ask_goal"
        return f"Nice to meet you, {user_state['name']}!\nWhat is your main financial goal right now?\n(For example: Save for school, Pay off debt, Build emergency fund, Budget better, Other)"

    if step == "ask_goal":
        user_state["goal"] = user_input.strip()
        user_state["step"] = "collect_income_0"
        return f"Thanks, {user_state['name']}!\nLet's start building your budget.\nHow much do you earn monthly from your Part-time job?"

    if step.startswith("collect_income_"):
        idx = int(step.split("_")[-1])
        category = income_categories[idx]
        user_state["income"][category] = extract_number(user_input)

        if idx + 1 < len(income_categories):
            user_state["step"] = f"collect_income_{idx + 1}"
            next_cat = income_categories[idx + 1]
            return f"Thanks!\nHow much do you receive monthly from {next_cat}?"
        else:
            user_state["step"] = "collect_expense_0"
            return f"Great!\nNow let's look at your expenses.\nHow much do you spend on Rent?"

    if step.startswith("collect_expense_"):
        idx = int(step.split("_")[-1])
        category = expense_categories[idx]
        user_state["expenses"][category] = extract_number(user_input)

        if idx + 1 < len(expense_categories):
            user_state["step"] = f"collect_expense_{idx + 1}"
            next_cat = expense_categories[idx + 1]
            return f"Got it.\nAnd how much do you spend on {next_cat}?"
        else:
            user_state["step"] = "summary"
            income = format_dict_as_bullet_list("Income", user_state["income"])
            expenses = format_dict_as_bullet_list("Expenses", user_state["expenses"])
            summary = (
                f"Here's your budget summary, {user_state['name']}:\n\n"
                f"{income}\n\n"
                f"{expenses}\n\n"
                "Would you like tailored insights about your financial management based on your goal?"
            )
            return summary

    if step == "summary":
        if any(word in user_input.lower() for word in ["yes", "yeah", "yep", "sure", "ok"]):
            user_state["insight_requested"] = True
            user_state["step"] = "insights"
            prompt = (
                f"My financial goal is: {user_state['goal']}\n"
                f"My income sources: {user_state['income']}\n"
                f"My expense categories: {user_state['expenses']}\n"
                "Based on this, give me insights or tips to improve my financial management as a student."
            )
            user_state["insight_text"] = conversation.predict(input=prompt)
            return user_state["insight_text"]
        else:
            return "No worries! Your budget template is ready.\nClick the 'Export Budget Spreadsheet' button if you'd like to download it."

    if step == "insights":
        return "Your budget is ready. Click the 'Export Budget Spreadsheet' button to download it."

    return conversation.predict(input=user_input)