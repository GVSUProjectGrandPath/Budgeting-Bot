
# REP4ⓇFinLit: AI Budgeting Assistant

**REP4ⓇFinLit** is an easy-to-use chatbot that helps you set financial goals, track your income and expenses, get AI-powered budgeting advice, and download a ready-to-use spreadsheet of your budget.

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
## Get the project to your local machine

   Follow instructions in the following link on how to clone a Git repository

   [Cloning a Git Repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)


Install Python (if needed)
[Download Python here](https://www.python.org/downloads/) -Python 3

Open a terminal and naviagte to the project folder:
   ```
   cd budgeting-bot
   ```

## Backend Setup

Setting Up the Backend (AI & API)

The backend powers the chatbot’s brain using Python and OpenAI.

1. Create and activate a Python virtual environment for the project:

   Example:
   ```
   python -m venv venv
   ```
   Activate the python virtual environment:

   a. On Windows
   ```
   venv\\Scripts\\activate 
   ```

   b. On Mac/Linux
   ```
   source venv/bin/activate
    ```

2. Install dependencies:

   You can also install dependencies from the project root

   Navigate to the backend 
   ```
   cd backend
   ```
   ```
   pip install -r requirements.txt
   ```
3. Add your OpenAI API key to a `.env` file in `backend/app`:

   This `.env` file has to be added to a `.gitignore` file when pushing the project to a public repository to prevent its contents from being exposed.

   ```
   cd backend/app
   ```
   Depending on the text editor you are using
   ```
   touch .env
   ```

   Log in to your OpenAI account and buy credits.

   Go to [Platform OpenAI](https://platform.openai.com/settings/organization/api-keys) 
   
   Create a new API key and copy it. Store it somewhere secure (once you leave the page, you will not access the API key again).

   Replace the 'xxxxx' in the code below with your API key and copy paste the line of code to your `.env` file
   ```
   OPENAI_API_KEY=sk-xxxxx
   ```
3. Run/start the FastAPI backend server:

   With your virtual environment active, run:

   Uvicorn was installed early in the dependencies installation.
   ```
   uvicorn app.main:app --reload --port 8000
   ```

   The backend will now run at [http://localhost:8000](http://localhost:8000)

## Frontend Setup (chat window)

Install Node.js (if needed)
[Download Node.js here](https://nodejs.org/).

1. Navigate to the frontend in a new terminal window:

   Ensure you are in the project root.
   ```
   cd frontend
   ```
   Run the following code in the same terminal window to get the frontend running
   ```
   npm install
   ```
   ```
   npm start
   ```
2. Open http://localhost:3000

   The chat will open at [http://localhost:3000](http://localhost:3000)

## Using REP4ⓇFinLit Chatbot
### The chatbot will walk you through:
  1. Entering your name
  2. Setting a financial goal
  3. Adding your income sources
  4. Adding your expenses
  5. Asking any money/budgeting questions
  6. Downloading your personalized budget spreadsheet

---

### Key Features

+ **Conversational stepper:** Easy, guided entry for name, goal, income, expenses, and more

+ **Personalized insights:** GPT-powered, based on your unique financial context

+ **Strict guardrails:** Only answers money/budgeting questions (politely declines off-topic ones)

+ **Beautiful, modern UI:** Styled for desktop and mobile, with auto-focus and quick navigation

+ **Spreadsheet download:** Export your budget as a ready-to-use Excel file

---

### Troubleshooting & Debugging Tips

**The chatbot doesn’t respond?**
  - Ensure both backend and frontend servers are running.
  - Make sure your OpenAI API key is correct and saved in `backend/app/.env`.

**“API Key” errors or no credits?**
  - Make sure your OpenAI key is valid and your account has credit.

**Download button doesn’t work?**
  - Try clicking the “Click here if your download does not start” link below the button.

**Still stuck?**
  - Check your `.env` setup
  - Restart your terminal, double-check your setup, and try again.
  - Add print statements to ensure:
  
      a. All AI context (name, goal, income, expenses) is sent in a single message for compatibility and transparency.  
      b. Both backend and frontend print debug info (see browser console and backend terminal).

---

### For Developers

+ Backend is Python (FastAPI); frontend is React (Create React App).

+ Only the `/chat` endpoint is used for AI requests; `/export-budget` for spreadsheet download.

+ Easy to extend for persistent sessions, authentication, or richer analytics.

+ Modify the React ChatWindow.jsx for custom questions, more categories, or additional logic.

---

### Acknowledgments

Powered by OpenAI, LangChain, FastAPI, and React.

Happy budgeting with REP4ⓇFinLit!