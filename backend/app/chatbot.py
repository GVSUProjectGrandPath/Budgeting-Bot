import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo-1106"

llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.7,
    api_key=openai_api_key,
    model_kwargs={"response_format": {"type": "json_object"}}
)

memory = ConversationBufferMemory(return_messages=True)
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

def build_json_system_prompt():
    return (
        "You are a helpful budgeting coach for college students. "
        "Always respond ONLY with a valid JSON object. "
        "The JSON must contain: "
        "'summary' (one or two short sentences summarizing the user's situation or answering the question), and "
        "'tips' (an array of 2-5 actionable, student-friendly, concrete budgeting tips—each under 25 words). "
        "Make tips positive, specific, and practical. "
        "Never include any text or formatting outside the JSON object."
        ' Example: {"summary": "...", "tips": ["...", "..."]}'
    )

def build_insights_prompt(name, goal, income, expenses):
    income_clean = {k: v if v not in [None, "None", ""] else 0 for k, v in income.items()}
    expenses_clean = {k: v if v not in [None, "None", ""] else 0 for k, v in expenses.items()}
    return (
        f"User: {name}\n"
        f"Goal: {goal}\n"
        f"Income: {income_clean}\n"
        f"Expenses: {expenses_clean}\n\n"
        "Please answer in JSON as described in the instructions."
    )

def build_qna_prompt(name, goal, income, expenses, qna):
    income_clean = {k: v if v not in [None, "None", ""] else 0 for k, v in income.items()}
    expenses_clean = {k: v if v not in [None, "None", ""] else 0 for k, v in expenses.items()}
    return (
        f"User: {name}\n"
        f"Goal: {goal}\n"
        f"Income: {income_clean}\n"
        f"Expenses: {expenses_clean}\n"
        f"Question: {qna}\n\n"
        "Please answer in JSON as described in the instructions."
    )

def get_structured_llm_response(messages):
    print("\n📤 [DEBUG] Calling OpenAI LLM with messages:")
    for m in messages:
        print(f"  {m['role']}: {m['content'][:300]}{'...' if len(m['content']) > 300 else ''}")
    response = conversation.llm.client.create(
        model=MODEL_NAME,
        messages=messages,
        response_format={"type": "json_object"}
    )
    print("\n📥 [DEBUG] Full raw LLM response:", response)
    return response.choices[0].message.content
