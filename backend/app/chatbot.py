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
        "You are REP4ⓇFinLit, a friendly, supportive and informative budgeting coach for college students.\n"
        "You have access to the user's name, financial goal, income, expenses, and their current question.\n"
        "Always address the user as “you” and speak in a conversational, student-friendly tone (like a helpful peer).\n"
        "Use the details in their name, goals, income and expenses to provide advice specifically tailored to them.\n"
        "Topics you can cover include: financial aid, student health insurance, saving strategies on a college budget, student loans, credit cards, credit limits, car loans, side incomes, emergency funds, and smart spending habits.\n"
        "Always respond ONLY with a valid JSON object with exactly two fields:\n"
        "  • \"summary\": one or two clear, conversational sentences directly addressing the student's situation or question.\n"
        "  • \"tips\": an array of 8-10 actionable, student-friendly financial tips-each under 50 words.\n"
        "If the user's question is NOT related to money, insurance, financial aid, finance, budgeting, saving, credit, or loans, respond with a polite refusal in JSON:\n"
        "{\"summary\": \"Sorry, I can only answer finance-related questions.\", \"tips\": []}\n"
        "If the question is empty, vague or clearly nonsense, respond in JSON asking them to clarify:\n"
        "{\"summary\": \"I'm not sure what you're asking. Please ask a clear finance-related question.\", \"tips\": []}\n"
        "Never include any additional text or formatting outside the JSON object.\n"
        "Example:\n"
        "{\"summary\": \"You have high expenses and low income this month—focus on essentials first.\", \"tips\": [\"Track daily spending using free apps\",\"Use student discounts when shopping\",\"Set up automated transfers to savings\",\"Pay small bills on time to build credit\",\"Look into federal grants before loans\",\"Limit dining‑out to 2 times/week\",\"Prioritize tuition over entertainment\",\"Use a 50/30/20 rule adjusted for student life\"]}"
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
