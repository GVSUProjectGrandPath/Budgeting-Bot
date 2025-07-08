import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "../styles.css";

const incomeSources = [
  "Job", "Side-hustle", "Family support", "Scholarships", "Reimbursements", "Tax refunds"
];
const expenseCategories = [
  "Rent", "Groceries", "Utilities", "Transport", "Tuition", "Dining out", "Entertainment", "Other"
];

export default function ChatWindow() {
  const [step, setStep] = useState(0);
  const [userState, setUserState] = useState({
    name: "", goal: "", income: {}, expenses: {}, qna: "", insights: ""
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatResponse, setChatResponse] = useState("");
  const [spreadsheetUrl, setSpreadsheetUrl] = useState("");

  // Auto-focus input on step/response change
  const inputRef = useRef(null);
  useEffect(() => {
    if (inputRef.current) inputRef.current.focus();
  }, [step, loading, chatResponse]);

  // Debug print for state
  useEffect(() => {
    console.log("🟢 Frontend state:", { step, userState });
  }, [step, userState]);

  // Stepper logic
  const handleNext = (field) => {
    setUserState(s => ({ ...s, [field]: input }));
    setInput("");
    setStep(step + 1);
  };

  const handleMultiNext = (field, key, value) => {
    setUserState(s => ({
      ...s,
      [field]: { ...s[field], [key]: value }
    }));
    setInput("");
    setStep(step + 1);
  };

  const sendLLM = async (stepName) => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/chat", {
        step: stepName,
        user_state: userState,
      });
      console.log("🟢 Frontend got:", res.data);
      setChatResponse(res.data.response);
      setUserState(s => ({
        ...s,
        last_bot_message: res.data.response,
        insight_text: stepName === "insights" ? res.data.response : s.insight_text
      }));
    } catch (err) {
      console.error(err);
      setChatResponse("Oops! Something went wrong.");
    }
    setLoading(false);
  };

  const download = async () => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/export-budget", userState, { responseType: "blob" });
      const url = URL.createObjectURL(new Blob([res.data]));
      setSpreadsheetUrl(url);
      console.log("🟢 Frontend downloaded spreadsheet");
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  // Step-by-step chat UI
  return (
    <div className="chat-window">
      {/* Step 0: Greeting */}
      {step === 0 && (
        <div className="bot-bubble">
          <h2>Hello, I am FinBot, your AI Budgeting Assistant.</h2>
          <button onClick={() => setStep(1)}>Start</button>
        </div>
      )}
      {/* Step 1: Name */}
      {step === 1 && (
        <div className="bot-bubble">
          <p>What is your name?</p>
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleNext("name")}
          />
          <button onClick={() => handleNext("name")}>Next</button>
        </div>
      )}
      {/* Step 2: Financial Goal */}
      {step === 2 && (
        <div className="bot-bubble">
          <p>What is your financial goal this month?</p>
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleNext("goal")}
          />
          <button onClick={() => handleNext("goal")}>Next</button>
        </div>
      )}
      {/* Step 3: Confirmation */}
      {step === 3 && (
        <div className="bot-bubble">
          <p>You wanna know what I think about your financial goal?</p>
          <button onClick={() => setStep(step + 1)}>Yes</button>
          <button onClick={() => setStep(step + 1)}>No</button>
        </div>
      )}
      {/* Income collection */}
      {step >= 4 && step < 4 + incomeSources.length && (() => {
        const idx = step - 4;
        const label = incomeSources[idx];
        return (
          <div className="bot-bubble">
            <p>How much do you get from {label}?</p>
            <input
              ref={inputRef}
              type="number"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && input && handleMultiNext("income", label, Number(input))}
            />
            <button
              onClick={() => input && handleMultiNext("income", label, Number(input))}
              disabled={!input}
            >
              Next
            </button>
          </div>
        );
      })()}
      {/* Expenses collection */}
      {step >= 4 + incomeSources.length && step < 4 + incomeSources.length + expenseCategories.length && (() => {
        const idx = step - (4 + incomeSources.length);
        const label = expenseCategories[idx];
        return (
          <div className="bot-bubble">
            <p>How much do you spend on {label}?</p>
            <input
              ref={inputRef}
              type="number"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && input && handleMultiNext("expenses", label, Number(input))}
            />
            <button
              onClick={() => input && handleMultiNext("expenses", label, Number(input))}
              disabled={!input}
            >
              Next
            </button>
          </div>
        );
      })()}
      {/* Insights */}
      {step === 4 + incomeSources.length + expenseCategories.length && (
        <div className="bot-bubble">
          <p>Insights for optimizing your money management skills</p>
          <button onClick={() => sendLLM("insights")} disabled={loading}>
            {loading ? "Thinking..." : "Get Insights"}
          </button>
          {chatResponse && <div className="insights">{chatResponse}</div>}
          {chatResponse && <button onClick={() => setStep(step + 1)}>Next</button>}
        </div>
      )}
      {/* Q&A */}
      {step === 5 + incomeSources.length + expenseCategories.length && (
        <div className="bot-bubble">
          <p>Do you have any questions about your money management or budgeting?</p>
          <input
            ref={inputRef}
            value={userState.qna}
            onChange={e => setUserState(s => ({ ...s, qna: e.target.value }))}
            onKeyDown={e => e.key === "Enter" && sendLLM("qna")}
          />
          <button onClick={() => sendLLM("qna")} disabled={loading}>
            {loading ? "Thinking..." : "Ask"}
          </button>
          {chatResponse && <div className="insights">{chatResponse}</div>}
          <button onClick={() => setStep(step + 1)}>Next</button>
        </div>
      )}
      {/* Spreadsheet download */}
      {step === 6 + incomeSources.length + expenseCategories.length && (
        <div className="bot-bubble">
          <p>Download your budget template as a spreadsheet</p>
          <button onClick={download} disabled={loading}>Download</button>
          {spreadsheetUrl && (
            <a href={spreadsheetUrl} download="budget.xlsx">Click here if your download does not start.</a>
          )}
        </div>
      )}
      {/* Done */}
      {step > 6 + incomeSources.length + expenseCategories.length && (
        <div className="bot-bubble"><p>Thank you for using FinBot! Refresh to start over.</p></div>
      )}
    </div>
  );
}
