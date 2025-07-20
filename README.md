# budgeting.ai: Your AI Budgeting Assistant

**budgeting.ai** is an easy-to-use chatbot that helps you set financial goals, track your income and expenses, get AI-powered budgeting advice, and download a ready-to-use spreadsheet of your budget.

---

## What’s in the Project?

```
Budgeting-AI/
├── backend/
│   └── app/
│       ├── main.py
│       ├── chatbot.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatWindow.jsx
│   │   ├── App.jsx
│   │   ├── index.js
│   │   └── styles.css
│   └── package.json
└── README.md
```

---

## Step 1: Setting Up the Backend (AI & API)

**The backend powers the chatbot’s brain using Python and OpenAI.**

### 1.1 Install Python (if needed)
- [Download Python here](https://www.python.org/downloads/).

### 1.2 Create and Activate a Virtual Environment
- Open a terminal/command prompt and run:
  ```
  python -m venv venv
  ```
- To activate:
  - On Windows:
    ```
    venv\Scripts\activate
    ```
  - On Mac/Linux:
    ```
    source venv/bin/activate
    ```

### 1.3 Install Backend Packages
- From the project root:
  ```
  pip install -r backend/requirements.txt
  ```

### 1.4 Get Your OpenAI API Key
- Go to [OpenAI API Keys](https://platform.openai.com/account/api-keys)
- Create a new key and copy it.

### 1.5 Add Your API Key to the Project
- In `backend/app/`, create a file called `.env`
- Add:
  ```
  OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxx
  ```

### 1.6 Start the Backend Server
- With your virtual environment active:
  ```
  uvicorn app.main:app --reload --port 8000
  ```
- The backend will now run at [http://localhost:8000](http://localhost:8000)

---

## Step 2: Setting Up the Frontend (Chat Window)

**The frontend is the friendly chat window you use in your browser.**

### 2.1 Install Node.js (if needed)
- [Download Node.js here](https://nodejs.org/).

### 2.2 Install Frontend Packages
- Open a new terminal window and go to the `frontend/` folder:
  ```
  cd frontend
  npm install
  ```

### 2.3 Start the Chat App
- In the same terminal:
  ```
  npm start
  ```
- The chat will open at [http://localhost:3000](http://localhost:3000)

---

## Step 3: Using budgeting.ai

- Go to [http://localhost:3000](http://localhost:3000)
- The chatbot will walk you through:
  1. Entering your name
  2. Setting a financial goal
  3. Adding your income sources
  4. Adding your expenses
  5. Asking any money/budgeting questions
  6. Downloading your personalized budget spreadsheet

---

## Features

- **Conversational, step-by-step chat** tailored for students
- **Personalized AI budgeting advice and tips**
- **Strict guardrails:** Only answers money/budgeting questions (politely declines off-topic ones)
- **Beautiful desktop/mobile UI**
- **Instant spreadsheet download**

---

## Troubleshooting

- **The chatbot doesn’t respond?**
  - Ensure both backend and frontend servers are running.
  - Make sure your OpenAI API key is correct and saved in `backend/app/.env`.

- **“API Key” errors or no credits?**
  - Make sure your OpenAI key is valid and your account has credit.

- **Download button doesn’t work?**
  - Try clicking the “Click here if your download does not start” link below the button.

- **Still stuck?**
  - Restart your terminal, double-check your setup, and try again.

---

## 🙏 Credits

Built with:
- Python, FastAPI, OpenAI, React, LangChain, OpenPyXL

---

**Enjoy smarter budgeting with FinBot!**  
Questions or issues? Review your setup steps above or reach out to your project lead.