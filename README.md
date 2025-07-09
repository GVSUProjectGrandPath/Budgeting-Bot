# PGPBOT - Financial Literacy Chatbot for Students 🎓💰

A beautiful, modern chatbot powered by Mistral AI that helps university students with all their financial literacy questions - from budgeting and student loans to investing and credit building.

![PGPBOT Demo](https://img.shields.io/badge/Status-Ready%20to%20Deploy-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue)
![AI Model](https://img.shields.io/badge/AI-Mistral%207B-purple)

## ✨ Features

- **🤖 Mistral AI Integration**: Powered by the efficient Mistral 7B model running locally
- **📊 Real-time Financial Data**: Fetches current interest rates, exchange rates, and more
- **🎯 Student-Focused**: Specialized knowledge for university students' financial needs
- **💬 Beautiful Chat Interface**: Modern, gradient-styled UI with smooth animations
- **🔒 Privacy-First**: Runs entirely on your local machine - no data sent to external servers
- **⚡ Fast & Responsive**: Streaming responses for real-time conversation feel
- **🧠 Conversation Memory**: Remembers your financial details throughout the conversation
- **📈 Smart Calculators**: Interactive tools for loans, budgets, investments, and more

## 🚀 Quick Start Guide for Windows

### Prerequisites
- Windows 10/11 with PowerShell
- Administrator access (for installations)
- At least 8GB RAM (for running Mistral model)
- 10GB free disk space

### Step 1: Download and Extract

1. Download/copy the entire PGPBOT folder to your PC
2. Open PowerShell as Administrator (Right-click → Run as Administrator)
3. Navigate to the PGPBOT folder:
   ```powershell
   cd C:\path\to\PGPBOT
   ```

### Step 2: Run Automated Setup

```powershell
# Allow script execution (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the setup script
.\setup-windows.ps1
```

This script will automatically:
- ✅ Install Chocolatey (package manager)
- ✅ Install Python 3.11
- ✅ Install Node.js
- ✅ Install Ollama
- ✅ Download Mistral AI model (~4GB)
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Create configuration files

**⏱️ Note:** The setup takes 15-30 minutes (mostly for downloading the Mistral model).

### Step 3: Start the Chatbot

```powershell
.\start-chatbot.ps1
```

This will:
1. Start Ollama service
2. Start the backend API server
3. Start the frontend React app
4. Open your browser to http://localhost:3000

## 📸 What You'll See

### Welcome Screen
A beautiful gradient background with a personalized name prompt to make the experience more engaging.

### Chat Interface
- Clean, modern design with purple gradient theme
- Smooth message animations
- Real-time typing indicators
- Responsive on all devices

## 💬 What Can You Ask?

The bot is equipped to help with ALL financial topics relevant to students:

### 🧠 Conversation Memory
The bot now remembers your conversation context! For example:
- Tell it your income: "I make $2000 per month from my part-time job"
- Share your expenses: "My rent is $800, food is $300, and transportation is $150"
- Later ask: "Based on my expenses, can you create a budget for me?"
- The bot will use your previously shared information!

### 📚 Topics Covered:
- **Budgeting**: Creating budgets, tracking expenses, saving money
- **Student Loans**: Federal loans, private loans, repayment options, forgiveness programs
- **Credit**: Building credit, credit cards, credit scores, credit reports
- **Investing**: Stocks, bonds, ETFs, index funds, 401k, IRA basics
- **Banking**: Checking/savings accounts, CDs, online banking
- **Financial Terms**: APR, APY, compound interest, etc.
- **Taxes**: Student tax filing, deductions, work-study income
- **Insurance**: Health, auto, renters insurance basics
- **Side Income**: Part-time jobs, internships, gig economy
- **Emergency Funds**: How much to save, where to keep it
- **Financial Technology**: Payment apps, budgeting apps, cryptocurrency basics

### 💡 Example Questions:
- "What is an ETF and should I invest in one?"
- "How can I start building my credit score?"
- "What's the current federal student loan interest rate?"
- "How much should I save for an emergency fund?"
- "Can you help me create a budget with $2000 monthly income?"
- "What's the difference between subsidized and unsubsidized loans?"
- "How do I file taxes as a student?"
- "Should I get a credit card in college?"

## 📁 Project Structure

```
PGPBOT/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI backend with Mistral integration
│   │   └── calculators.py   # Financial calculators
│   ├── requirements.txt     # Python dependencies
│   └── .env                # Backend configuration (created by setup)
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # React chat interface
│   │   ├── App.css         # Beautiful gradient styles
│   │   ├── index.tsx       # React entry point
│   │   └── index.css       # Base styles
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── package.json        # Node dependencies
│   └── .env.local          # Frontend configuration (created by setup)
├── setup-windows.ps1       # One-time setup script
├── start-chatbot.ps1       # Start script
└── README.md              # This file
```

## 🛠️ Manual Setup (If Automated Setup Fails)

<details>
<summary>Click to expand manual setup instructions</summary>

### 1. Install Required Software

```powershell
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Python, Node.js, and Git
choco install python311 nodejs-lts git -y

# Download and install Ollama from https://ollama.com/download/windows
```

### 2. Set Up Ollama and Mistral

```powershell
# Start Ollama service
ollama serve

# In a new PowerShell window, pull Mistral model
ollama pull mistral:7b-instruct-q4_K_M
```

### 3. Set Up Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create .env file with:
# OLLAMA_URL=http://localhost:11434
# MODEL_NAME=mistral:7b-instruct-q4_K_M
```

### 4. Set Up Frontend

```powershell
cd frontend
npm install

# Create .env.local file with:
# REACT_APP_API_URL=http://localhost:8000
```

### 5. Run the Application

```powershell
# Terminal 1: Backend
cd backend
.\venv\Scripts\Activate.ps1
python app/main.py

# Terminal 2: Frontend
cd frontend
npm start
```

</details>

## 🔧 Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Cannot find path specified" | Ensure you're in the correct directory and all files exist |
| "Module not found" | Activate venv: `.\venv\Scripts\Activate.ps1` then reinstall: `pip install -r requirements.txt` |
| Ollama Connection Error | Ensure Ollama is running: `ollama serve` |
| Frontend Build Errors | Delete `node_modules` and run `npm install` again |
| Port Already in Use | Find process: `netstat -ano \| findstr :8000` then kill it: `taskkill /PID <PID> /F` |

## 🎯 Real-time Data Sources

The bot fetches real-time data from:
- **Federal Reserve Economic Data (FRED)**: Interest rates, economic indicators
- **Exchange Rate API**: Currency exchange rates
- **Static Updates**: Current student loan rates, savings account rates

## 🔒 Privacy & Security

- ✅ **100% Local**: Mistral model runs entirely on your machine
- ✅ **No Data Collection**: Your conversations are never stored or sent anywhere
- ✅ **No Account Required**: Start using immediately without sign-up
- ✅ **Open Source**: Full transparency in how the bot works

## 🤝 Contributing

Feel free to enhance the bot by:
- Adding more real-time data sources
- Improving the UI/UX
- Adding more financial calculators
- Expanding the knowledge base

## 📝 License

This project is open source and available under the MIT License.

## 🎉 Ready to Start?

Your financial literacy journey begins now! Run the setup script and start asking questions. The bot is here to help you make informed financial decisions throughout your university years and beyond.

```powershell
# Get started in one line:
.\setup-windows.ps1 && .\start-chatbot.ps1
```

---

**Made with ❤️ for students who want to master their finances** 