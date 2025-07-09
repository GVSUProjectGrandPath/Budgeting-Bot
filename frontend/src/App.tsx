import React, { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}


function App() {
  // Global configuration
  const botDisplayName = 'pgpfinlitbot'; // Default: "pgpfinlitbot". Fallback to "FinBot" if undefined.
  
  // Simple i18n helper (placeholder for future implementation)
  const t = (key: string, fallback: string) => fallback;

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: `Hi! I'm ${botDisplayName}, your financial literacy assistant. What would you like to know about budgeting, student loans, saving, or building credit?`,
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userName, setUserName] = useState('');
  const [showNamePrompt, setShowNamePrompt] = useState(true);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [latency, setLatency] = useState<number>(0);
  const [quickActionsVisible, setQuickActionsVisible] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const composerRef = useRef<HTMLDivElement>(null);
  const quickActionsRef = useRef<HTMLDivElement>(null);

  // Quick action questions
  const quickActions = [
    "What's the current student loan interest rate?",
    "How do I build credit as a student?",
    "Create a budget for me",
    "Should I invest while in college?",
    "Calculate my loan payments",
    "What is an ETF?"
  ];

  // Theme management
  useEffect(() => {
    // Check for saved theme preference or default to system preference
    const savedTheme = localStorage.getItem('pgpbot_theme') as 'light' | 'dark' | null;
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    
    const initialTheme = savedTheme || systemTheme;
    setTheme(initialTheme);
    document.documentElement.setAttribute('data-theme', initialTheme);

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      if (!savedTheme) {
        const newTheme = e.matches ? 'dark' : 'light';
        setTheme(newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
      }
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
  }, []);

  // Toggle theme
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('pgpbot_theme', newTheme);
  };

  // Latency-based header hue shift
  useEffect(() => {
    if (latency > 0) {
      const hueShift = Math.min(latency / 10, 60); // Max 60 degree shift for high latency
      document.documentElement.style.setProperty(
        '--header-bg', 
        `hsl(${latency > 500 ? 0 : 51 - hueShift}, 100%, ${theme === 'dark' ? '25%' : '50%'})`
      );
    }
  }, [latency, theme]);

  const loadConversationHistory = useCallback(async (convId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/conversation/${convId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.messages && data.messages.length > 0) {
          const historicalMessages: Message[] = data.messages.map((msg: any, index: number) => ({
            id: `history-${index}`,
            text: msg.content,
            sender: msg.role.toLowerCase() === 'user' ? 'user' : 'bot',
            timestamp: new Date(msg.timestamp)
          }));
          
          setMessages([
            {
              id: '1',
              text: `Welcome back, ${userName}! I'm ${botDisplayName} and I remember our previous conversation. How can I continue helping you with your finances? The financial summary I have is:\n\n${data.financial_summary}`,
              sender: 'bot',
              timestamp: new Date()
            },
            ...historicalMessages.slice(-10)
          ]);
        }
      }
    } catch (error) {
      console.error('Error loading conversation history:', error);
    }
  }, [userName]);

  // Load conversation ID from localStorage on mount
  useEffect(() => {
    const savedConversationId = localStorage.getItem('pgpbot_conversation_id');
    const savedUserName = localStorage.getItem('pgpbot_user_name');
    
    if (savedUserName) {
      setUserName(savedUserName);
      setShowNamePrompt(false);
    }
    
    if (savedConversationId) {
      setConversationId(savedConversationId);
      // Optionally load conversation history
      loadConversationHistory(savedConversationId);
    }
  }, [loadConversationHistory]);

  // IntersectionObserver to hide quick actions when composer is in view (Angle A)
  useEffect(() => {
    if (!composerRef.current || !quickActionsRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          // Hide quick actions when composer is intersecting (in view)
          setQuickActionsVisible(!entry.isIntersecting);
        });
      },
      {
        root: null,
        threshold: 0.1, // Trigger when 10% of composer is visible
      }
    );

    observer.observe(composerRef.current);

    return () => observer.disconnect();
  }, [showNamePrompt]); // Re-run when switching between name prompt and chat

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleNameSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (userName.trim()) {
      setShowNamePrompt(false);
      localStorage.setItem('pgpbot_user_name', userName);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: `Nice to meet you, ${userName}! I'm ${botDisplayName}, and I'm here to help. What financial topic can I help you with today?`,
        sender: 'bot',
        timestamp: new Date()
      }]);
    }
  };

  const handleQuickAction = (question: string) => {
    setInputText(question);
    // Optionally, directly send the message
    sendMessage(null, question);
  };

  const sendMessage = async (e: React.FormEvent | null, quickMessage?: string) => {
    if (e) e.preventDefault();
    const messageToSend = quickMessage || inputText;
    if (!messageToSend.trim() || isLoading) return;

    const startTime = Date.now();

    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageToSend,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    // Create bot message placeholder
    const botMessageId = (Date.now() + 1).toString();
    const botMessage: Message = {
      id: botMessageId,
      text: '',
      sender: 'bot',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, botMessage]);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          msg: messageToSend,
          user_name: userName || 'there',
          conversation_id: conversationId
        }),
      });

      // Calculate latency
      const endTime = Date.now();
      setLatency(endTime - startTime);

      if (response.status === 403) {
        const errorData = await response.json();
        throw new Error(errorData.detail.error || 'Request forbidden.');
      }
      if (!response.ok) throw new Error('Failed to get response');

      // Get conversation ID from response headers if not already set
      const responseConversationId = response.headers.get('X-Conversation-ID');
      if (responseConversationId && !conversationId) {
        setConversationId(responseConversationId);
        localStorage.setItem('pgpbot_conversation_id', responseConversationId);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          let hasUpdate = false;
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.token) {
                  accumulatedText += data.token;
                  hasUpdate = true;
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e);
              }
            }
          }
          if (hasUpdate) {
            // eslint-disable-next-line no-loop-func
            setMessages(prev => prev.map(msg => 
              msg.id === botMessageId 
                ? { ...msg, text: accumulatedText }
                : msg
            ));
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === botMessageId 
          ? { ...msg, text: `Sorry, I encountered an error: ${error instanceof Error ? error.message : String(error)}` }
          : msg
      ));
    } finally {
      setIsLoading(false);
      // Reset latency after a delay
      setTimeout(() => setLatency(0), 5000);
    }
  };

  const clearConversation = () => {
    // eslint-disable-next-line no-restricted-globals
    if (confirm('Are you sure you want to start a new conversation? This will clear your chat history.')) {
      localStorage.removeItem('pgpbot_conversation_id');
      setConversationId(null);
      setMessages([{
        id: Date.now().toString(),
        text: `Hi ${userName}! I'm ${botDisplayName}, and I'm here to help. What financial topic can I help you with today?`,
        sender: 'bot',
        timestamp: new Date()
      }]);
    }
  };

  // Function to generate dummy messages for testing
  const generateDummyMessages = () => {
    const dummyMessages: Message[] = [];
    for (let i = 1; i <= 100; i++) {
      dummyMessages.push({
        id: `dummy-${i}`,
        text: `This is dummy message #${i}. Lorem ipsum dolor sit amet, consectetur adipiscing elit.`,
        sender: i % 3 === 0 ? 'user' : 'bot',
        timestamp: new Date(Date.now() - (100 - i) * 60000), // Messages 1 minute apart
      });
    }
    setMessages(dummyMessages);
  };

  // Name prompt screen
  if (showNamePrompt) {
    return (
      <div className="app">
        <div className="name-prompt">
          <div className="name-prompt-card">
            <h1>Welcome to {botDisplayName}! 🎓💰</h1>
            <p>Your personal financial literacy assistant for students</p>
            <form onSubmit={handleNameSubmit} className="name-form">
              <input
                type="text"
                placeholder="What's your first name?"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                className="name-input"
                autoFocus
                aria-label="Enter your first name"
              />
              <button type="submit" className="name-submit">Get Started</button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // Main chat interface
  return (
    <div className="app">
      {/* Header with theme toggle and status indicator */}
      <header className="header" role="banner">
        <div className="header-content">
          <div className="header-title">
            <span>{botDisplayName} 🎓💰</span>
            <div 
              className="status" 
              title={`Backend status: ${latency > 500 ? 'slow' : 'good'} (${latency}ms)`}
              aria-label={`Backend response time: ${latency} milliseconds`}
            />
          </div>
          <div className="header-controls">
            <button 
              onClick={generateDummyMessages}
              className="theme-toggle"
              aria-label="Generate 100 test messages"
              title="Generate 100 test messages"
            >
              Test
            </button>
            <button 
              onClick={toggleTheme}
              className="theme-toggle"
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            >
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
            <button 
              onClick={clearConversation}
              className="theme-toggle restart-button"
              aria-label="Start new conversation"
              title="Start new conversation"
            >
              <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.49-.58 2.84-1.53 3.87l1.45 1.45C19.34 15.36 20 13.76 20 12c0-4.42-3.58-8-8-8zm-8 6c0-1.49.58-2.84 1.53-3.87l-1.45-1.45C4.66 8.64 4 10.24 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3c-3.31 0-6-2.69-6-6z"/>
              </svg>
              <span className="hide-on-mobile">New Chat</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main content area */}
      <div className="content-wrapper">
        <main className="main-container">
          {/* Chat column (66% width) */}
          <div className="chat-column">
            <div className="chat" role="log" aria-live="polite" aria-label="Chat messages">
              <div className="messages">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`bubble ${message.sender}`}
                    role={message.sender === 'bot' ? 'status' : undefined}
                  >
                    <div className="message-content">
                      {message.sender === 'bot' ? (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {message.text}
                        </ReactMarkdown>
                      ) : (
                        message.text
                      )}
                    </div>
                    <div className="message-time">
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="bubble bot">
                    <div className="typing-indicator" aria-label="Bot is typing">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Message composer - sticky at bottom */}
            <div className="composer-wrapper" ref={composerRef}>
              <form onSubmit={sendMessage} className="composer">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Ask a financial question..."
                  className="input-field"
                  disabled={isLoading}
                  aria-label="Type your message"
                />
                <button 
                  type="submit" 
                  className="send-button" 
                  disabled={isLoading || !inputText.trim()}
                  aria-label="Send message"
                >
                  <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                  </svg>
                </button>
              </form>
            </div>
          </div>

          {/* Sidebar column (34% width) */}
          <aside className="sidebar-column" aria-label={`Sidebar—${botDisplayName}`}>
            <div className="sidebar-card">
              <h3 className="sidebar-heading" data-testid={`sidebar-heading-${botDisplayName}`}>
                {t('botName', botDisplayName)}
              </h3>
              <p className="sidebar-sub">Personal financial-literacy assistant</p>
              <div className="progress" role="progressbar" aria-label="Conversation progress"></div>
            </div>
            
            <div className="sidebar-card">
              <h3 className="sidebar-title">Topics I can help with</h3>
              <ul>
                <li>📊 Budgeting & Planning</li>
                <li>🎓 Student Loans</li>
                <li>💳 Building Credit</li>
                <li>💰 Saving Strategies</li>
                <li>📈 Investment Basics</li>
                <li>🧮 Financial Calculations</li>
              </ul>
            </div>

            <div className="sidebar-card">
              <h3 className="sidebar-title">Status</h3>
              <p>
                <span className="status" style={{ display: 'inline-block', marginRight: '8px' }}></span>
                {latency > 0 ? `Response time: ${latency}ms` : 'Ready to help'}
              </p>
            </div>
          </aside>
        </main>

        {/* Quick action chips - outside main container */}
        <div 
          className={`quick-actions ${!quickActionsVisible ? 'hidden' : ''}`}
          role="group" 
          aria-label="Quick questions"
          ref={quickActionsRef}
        >
          {quickActions.map((action, index) => (
            <button
              key={index}
              className="quick-chip"
              onClick={() => handleQuickAction(action)}
              disabled={isLoading}
              aria-label={`Ask: ${action}`}
            >
              {action}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App; 