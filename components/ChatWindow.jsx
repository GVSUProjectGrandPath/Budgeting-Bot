import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import botAvatar from '../assets/bot.png';
import userAvatar from '../assets/user.png';
import '../styles.css';

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState('light');
  const messagesEndRef = useRef(null);

  const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light');

  const sendMessage = async () => {
    if (!input.trim()) return;

    const updatedMessages = [...messages, { role: "user", content: input }];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/chat-function-call", updatedMessages);
      const { action, message } = res.data;

      if (action === "respond") {
        setMessages(prev => [...prev, { role: "assistant", content: message }]);
      } else if (action === "export") {
        setMessages(prev => [...prev, { role: "assistant", content: message }]);
        setTimeout(() => {
          window.location.href = "http://localhost:8000/download";
        }, 1000);
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [...prev, { role: "assistant", content: "Oops! Something went wrong." }]);
    }

    setLoading(false);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className={`chat-window ${theme}`}>
      <button onClick={toggleTheme} className="theme-toggle">
        Switch to {theme === "dark" ? "Light" : "Dark"} Mode
      </button>
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <img src={msg.role === 'user' ? userAvatar : botAvatar} alt="avatar" className="avatar" />
            <div className="bubble"><strong>{msg.role === 'user' ? 'You' : 'FinBot'}:</strong> {msg.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <img src={botAvatar} alt="avatar" className="avatar" />
            <div className="bubble typing"><span>.</span><span>.</span><span>.</span></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="controls">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}