from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
import uuid
import os
from dotenv import load_dotenv

from .chatbot import conversation, user_state

# Load environment variables
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    step: str
    user_state: dict

@app.post("/chat")
def chat(req: ChatRequest):
    print("🟢 Backend received:", req.dict())
    step = req.step
    state = req.user_state
    name = state.get("name", "")
    goal = state.get("goal", "")
    income = state.get("income", {})
    expenses = state.get("expenses", {})
    qna = state.get("qna", "")
    response = ""

    if step == "insights":
        prompt = (
            f"Hi, my name is {name}. My financial goal: {goal}.\n"
            f"Income: {income}\nExpenses: {expenses}\n\n"
            "Please provide actionable, personalized insights or tips to help me improve my money management and budgeting."
        )
        response = conversation.predict(input=prompt)
        state["insight_text"] = response
        state["insight_requested"] = True

    elif step == "qna":
        prompt = (
            f"User {name} asks: \"{qna}\".\n"
            f"Goal: {goal}; Income: {income}; Expenses: {expenses}.\n"
            "Answer ONLY if it's about money management or budgeting. Otherwise politely refuse."
        )
        response = conversation.predict(input=prompt)

    else:
        response = "Unsupported step."

    return {"response": response}

def style_cell(cell, bold=False):
    cell.font = Font(bold=bold)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    cell.border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"),
    )

@app.post("/export-budget")
def export_budget(data: dict = user_state):
    print("🟢 Exporting budget with data:", data)
    wb = Workbook()
    ws = wb.active
    ws.title = "Budget Summary"

    def write_section(title, rows):
        ws.append([])
        ws.append([title])
        style_cell(ws.cell(row=ws.max_row, column=1), bold=True)
        for row in rows:
            ws.append(row)
            for col in range(1, len(row) + 1):
                style_cell(ws.cell(row=ws.max_row, column=col))

    write_section("Financial Goal", [[data.get("goal", "N/A")]])

    income_rows = [["Source", "Amount ($)"]] + [[src, amt] for src, amt in data.get("income", {}).items()]
    write_section("Income Sources", income_rows)

    expense_rows = [["Category", "Amount ($)"]] + [[cat, amt] for cat, amt in data.get("expenses", {}).items()]
    write_section("Expense Categories", expense_rows)

    total_income = sum(data.get("income", {}).values())
    total_expenses = sum(data.get("expenses", {}).values())
    write_section("Summary", [
        ["Total Income", total_income],
        ["Total Expenses", total_expenses],
        ["Net Balance", total_income - total_expenses]
    ])

    feedback_prompt = (
        f"My income: {data['income']}\nMy expenses: {data['expenses']}\n"
        f"My net balance: {total_income - total_expenses}.\n"
        "How would you summarize this financial picture for a college student?"
    )
    fb = conversation.predict(input=feedback_prompt)
    write_section("GPT Feedback", [[line] for line in fb.splitlines() if line.strip()])

    if data.get("insight_requested") and data.get("insight_text"):
        insights = [
            line.strip().lstrip('-• ') for line in data["insight_text"].splitlines()
            if line.strip()
        ]
        write_section("Insights / Recommendations", [[f"• {l}"] for l in insights])

    os.makedirs("downloads", exist_ok=True)
    filename = f"budget_{uuid.uuid4().hex[:8]}.xlsx"
    filepath = os.path.join("downloads", filename)
    wb.save(filepath)

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
