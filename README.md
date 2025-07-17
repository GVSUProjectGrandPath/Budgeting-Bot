
# FinBot: AI Budgeting Assistant

## Backend Setup
1. Create a Python virtual environment for the project:
   Example:
   ```
   python -m venv venv
   ```

   ```
   venv\\Scripts\\activate 
   ```
2. Install Python dependencies:
   ```
   pip install -r backend/requirements.txt
   ```
3. Add your OpenAI API key to a `.env` file in `backend/app`:

   Log in to your OpenAI account and buy credits.
   Go to [Platform OpenAI](https://platform.openai.com/settings/organization/api-keys) and press/create 'Create new secret key'
   ```
   OPENAI_API_KEY=sk-xxxxxxx
   ```
3. Run the FastAPI backend:
   ```
   uvicorn app.main:app --reload
   ```

## Frontend Setup
1. Go to `frontend/`:
   ```
   cd frontend
   npm install
   npm start
   ```
2. Open http://localhost:3000

Enjoy an easy-to-use, visually appealing, step-by-step budgeting experience!



🚀 FinBot – AI Budgeting Assistant
FinBot is a modern, interactive financial chatbot that helps you set goals, track income and expenses, and get AI-powered budgeting insights—step by step!

📁 Project Structure
pgsql
Copy
Edit
FinBot/
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
🛠 Backend Setup (FastAPI + OpenAI)
Install dependencies:

bash
Copy
Edit
pip install -r backend/requirements.txt
Create your OpenAI API key:

Sign up at https://platform.openai.com/

Get your API key and create a .env file in backend/app/:

ini
Copy
Edit
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Run the backend:

bash
Copy
Edit
uvicorn app.main:app --reload
By default runs at: http://localhost:8000

🌐 Frontend Setup (React)
Install dependencies:

bash
Copy
Edit
cd frontend
npm install
Start the React app:

bash
Copy
Edit
npm start
App will be at: http://localhost:3000

✨ Key Features
Conversational stepper: Easy, guided entry for name, goal, income, expenses, and more

Personalized insights: GPT-powered, based on your unique financial context

Strict money/budgeting Q&A: Only answers questions about financial topics

Beautiful, modern UI: Styled for desktop and mobile, with auto-focus and quick navigation

Spreadsheet download: Export your budget as a ready-to-use Excel file

⚡️ Development & Debugging Tips
All AI context (name, goal, income, expenses) is sent in a single message for compatibility and transparency.

Both backend and frontend print debug info (see browser console and backend terminal).

Modify the React ChatWindow.jsx for custom questions, more categories, or additional logic.

🧑‍💻 For Developers
Backend is Python (FastAPI); frontend is React (Create React App).

Only the /chat endpoint is used for AI requests; /export-budget for spreadsheet download.

Easy to extend for persistent sessions, authentication, or richer analytics.

🙏 Acknowledgments
Powered by OpenAI, LangChain, FastAPI, and React.

Happy budgeting with FinBot!
If you get stuck, check your .env setup and that your backend/React servers are both running.