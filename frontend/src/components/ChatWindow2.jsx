import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import botAvatar from "../assets/bot.png";
import userAvatar from "../assets/user.png";
import "../styles.css";

// Step constants
const STEPS = {
  NAME: 0,
  GOAL: 1,
  INCOME_START: 2,
  EXPENSE_START: 8, // (income fields count + 2)
  QNA: 16,          // (income + expense fields count + 2)
  DOWNLOAD: 17      // one after QNA
};

const incomeSources = [
  "Job", "Side-hustle", "Family support", "Scholarships", "Reimbursements", "Tax refunds"
];
const expenseCategories = [
  "Rent", "Groceries", "Utilities", "Transport", "Tuition", "Dining out", "Entertainment", "Other"
];

export default function ChatWindow() {
  const [theme, setTheme] = useState("light");
  const [fontSize, setFontSize] = useState(1.0);
  const [step, setStep] = useState(STEPS.NAME);
  const [userState, setUserState] = useState({
    name: "",
    goal: "",
    income: {},
    expenses: {},
    qna: ""
  });
  const [input, setInput] = useState("");
  const [qaInput, setQaInput] = useState("");
  const [qaResponse, setQaResponse] = useState(null);
  const [spreadsheetUrl, setSpreadsheetUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const [messages, setMessages] = useState([
    { from: "bot", text: "Hello, I am FinBot, your AI Budgeting Assistant.\nGet ready to answer some questions.\n What is your name?" }
  ]);
  const inputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (inputRef.current) inputRef.current.focus();
  }, [step, loading, qaResponse]);

  useEffect(() => {
    if (chatEndRef.current) chatEndRef.current.scrollIntoView({ behavior: "smooth" });
  }, [messages, qaResponse, loading]);

  const handleRestart = () => {
    setMessages([
      { from: "bot", text: "Hello, I am FinBot, your AI Budgeting Assistant.\nGet ready to answer some questions.\n What is your name?" }
    ]);
    setStep(STEPS.NAME);
    setUserState({
      name: "",
      goal: "",
      income: {},
      expenses: {},
      qna: ""
    });
    setInput("");
    setQaInput("");
    setQaResponse(null);
    setSpreadsheetUrl("");
  };

  const addMessage = (from, text) => {
    setMessages(prev => [...prev, { from, text }]);
  };

  // Stepper logic
  const handleBudgetStepper = () => {
    if (!input.trim()) return;
    if (step === STEPS.NAME) {
      addMessage("user", input);
      setUserState(s => ({ ...s, name: input }));
      setInput("");
      setTimeout(() => {
        addMessage("bot", "What is your main financial goal this month?");
        setStep(STEPS.GOAL);
      }, 350);
    } else if (step === STEPS.GOAL) {
      addMessage("user", input);
      setUserState(s => ({ ...s, goal: input }));
      setInput("");
      setTimeout(() => {
        addMessage("bot", `How much do you get monthly from your ${incomeSources[0]}?`);
        setStep(STEPS.INCOME_START);
      }, 350);
    } else if (step >= STEPS.INCOME_START && step < STEPS.EXPENSE_START) {
      const idx = step - STEPS.INCOME_START;
      addMessage("user", `$${input} from ${incomeSources[idx]}`);
      setUserState(s => ({
        ...s,
        income: { ...s.income, [incomeSources[idx]]: Number(input) }
      }));
      setInput("");
      if (idx + 1 < incomeSources.length) {
        setTimeout(() => {
          addMessage("bot", `How much do you get monthly from your ${incomeSources[idx + 1]}?`);
          setStep(step + 1);
        }, 350);
      } else {
        setTimeout(() => {
          addMessage("bot", `How much do you spend monthly on ${expenseCategories[0]}?`);
          setStep(STEPS.EXPENSE_START);
        }, 350);
      }
    } else if (step >= STEPS.EXPENSE_START && step < STEPS.QNA) {
      const idx = step - STEPS.EXPENSE_START;
      addMessage("user", `$${input} for ${expenseCategories[idx]}`);
      setUserState(s => ({
        ...s,
        expenses: { ...s.expenses, [expenseCategories[idx]]: Number(input) }
      }));
      setInput("");
      if (idx + 1 < expenseCategories.length) {
        setTimeout(() => {
          addMessage("bot", `How much do you spend monthly on ${expenseCategories[idx + 1]}?`);
          setStep(step + 1);
        }, 350);
      } else {
        setTimeout(() => {
          addMessage("bot", "All set! Now you can ask me any question about your income, spending or money management.\n I'll give you actionable tips based on your info.");
          setStep(STEPS.QNA);
        }, 350);
      }
    }
  };

  // Q&A logic
  const QNA_STEP = 16; // Should match STEPS.QNA in your backend

const askQuestion = async () => {
  setLoading(true);
  addMessage("user", qaInput);

  try {
    // Send the required shape: { step, user_state }
    const res = await axios.post("http://localhost:8000/chat", {
      step: QNA_STEP,
      user_state: {
        name: userState.name,
        goal: userState.goal,
        income: userState.income,
        expenses: userState.expenses,
        qna: qaInput
      }
    });

    setQaResponse(res.data.response);
    addMessage("bot", typeof res.data.response === "string" ? res.data.response : res.data.response.summary);
    setQaInput("");
  } catch (error) {
    setQaResponse("Sorry, could not get an answer.");
    addMessage("bot", "Sorry, could not get an answer.");
  }
  setLoading(false);
};

  // Download spreadsheet
  const downloadSpreadsheet = async () => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/export-budget", userState, { responseType: "blob" });
      const url = URL.createObjectURL(new Blob([res.data]));
      setSpreadsheetUrl(url);
      addMessage("bot", "Your budget spreadsheet is ready!");
    } catch (err) {
      alert("Download failed.");
    }
    setLoading(false);
  };

  const fontSizePct = Math.round(fontSize * 100);

  // Chat rendering (with CSS Grid for avatars and bubbles)
  return (
    <div className={`chat-window-modern ${theme}`} style={{ fontSize: `${fontSize}em` }}>
      <div className="theme-toggle-row">
        <button
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          className="theme-toggle-btn"
          tabIndex={0}
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          {theme === "dark" ? "Light" : "Dark"}
        </button>
        <button
          aria-label={`Increase font size (current: ${fontSizePct}%)`}
          className="font-size-btn"
          tabIndex={0}
          style={{ marginLeft: 8 }}
          onClick={() => setFontSize(f => Math.min(f + 0.15, 1.7))}
        >+</button>
        <button
          aria-label={`Decrease font size (current: ${fontSizePct}%)`}
          className="font-size-btn"
          tabIndex={0}
          style={{ marginLeft: 2 }}
          onClick={() => setFontSize(f => Math.max(f - 0.15, 0.7))}
        >-</button>
        <button
          className="restart-btn"
          tabIndex={0}
          aria-label="Restart conversation"
          style={{ marginLeft: 16 }}
          onClick={handleRestart}
        >Restart</button>
      </div>
      <div className="chat-scrollbox gradient-bg">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`bubble-row ${msg.from === "user" ? "right" : "left"}`}
          >
            <div className="bubble-grid">
              <img
                src={msg.from === "user" ? userAvatar : botAvatar}
                alt={msg.from === "user" ? "User avatar" : "FinBot avatar"}
                className="bubble-avatar"
              />
              <div
                className={msg.from === "user" ? "user-bubble bubble-animate" : "bot-bubble bubble-animate"}
                tabIndex={0}
                role="status"
                aria-live="polite"
              >
                <span style={{ flex: 1 }}>{msg.text}</span>
              </div>
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* === Stepper logic for wizard === */}
      {(step === STEPS.NAME || step === STEPS.GOAL ||
        (step >= STEPS.INCOME_START && step < STEPS.EXPENSE_START) ||
        (step >= STEPS.EXPENSE_START && step < STEPS.QNA)) && (
        <div className="input-row">
          <input
            ref={inputRef}
            type={step >= STEPS.INCOME_START && step < STEPS.QNA ? "number" : "text"}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleBudgetStepper()}
            aria-label="Your answer"
            style={{ flex: 1, minWidth: 0 }}
            disabled={loading}
            tabIndex={0}
          />
          <button
            className="bubble-action-btn"
            onClick={handleBudgetStepper}
            disabled={loading || !input.trim()}
            aria-label="Send"
            tabIndex={0}
          >
            Send
          </button>
        </div>
      )}

      {/* === Q&A Step === */}
      {step === STEPS.QNA && (
        <div className="bot-bubble bubble-animate">
          {!qaResponse && (
            <>
              <label htmlFor="qna-input">Ask a question about your budget or money:</label>
              <input
                id="qna-input"
                type="text"
                ref={inputRef}
                value={qaInput}
                onChange={e => setQaInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && askQuestion()}
                aria-label="Your budgeting question"
                style={{ marginTop: 6, marginBottom: 10 }}
                disabled={loading}
              />
              <button
                className="bubble-action-btn"
                onClick={askQuestion}
                disabled={loading || !qaInput.trim()}
              >
                {loading ? "Thinking..." : "Ask"}
              </button>
            </>
          )}
          {qaResponse && (
            <>
              <div style={{ marginBottom: 10 }}>
                <strong>Answer:</strong>
                <div style={{ marginTop: 6, marginBottom: 10 }}>{qaResponse}</div>
              </div>
              <div style={{ display: "flex", gap: 10 }}>
                <button
                  className="bubble-action-btn"
                  onClick={() => {
                    setQaResponse(null);
                    setQaInput("");
                  }}
                >
                  Ask another question
                </button>
                <button
                  className="bubble-action-btn"
                  onClick={() => setStep(STEPS.DOWNLOAD)}
                >
                  Finish & Download Budget Spreadsheet
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* === Download Step === */}
      {step === STEPS.DOWNLOAD && (
        <div className="bot-bubble bubble-animate">
          <p>Download your budget template as a spreadsheet</p>
          <button
            className="bubble-action-btn"
            onClick={downloadSpreadsheet}
            disabled={loading}
          >
            Download
          </button>
          {spreadsheetUrl && (
            <a href={spreadsheetUrl} download="budget.xlsx">Click here if your download does not start.</a>
          )}
        </div>
      )}
    </div>
  ); 
}
