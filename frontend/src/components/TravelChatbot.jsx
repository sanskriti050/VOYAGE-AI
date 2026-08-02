import { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "../services/api";

const QUICK_PROMPTS = [
  "Where should I eat now?",
  "Find nearby ATM",
  "It started raining, what now?",
  "Best local dish to try?",
  "How to get around here?",
  "Is it safe to travel solo?",
  "Shift today's plan",
  "Budget tips for this trip",
];

function TypingIndicator() {
  return (
    <div className="chat-msg chat-msg-ai">
      <div className="chat-avatar">🤖</div>
      <div className="chat-bubble typing-bubble">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
      </div>
    </div>
  );
}

function TravelChatbot({ tripContext = null }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: tripContext
        ? `Hi! I'm your VoyageAI Travel Assistant ✈️\n\nI can see you're planning a trip to **${tripContext.destination}**. Ask me anything — food spots, weather, ATMs, plan changes, local tips!`
        : "Hi! I'm your VoyageAI Travel Assistant ✈️\n\nAsk me anything about your trip — food, weather, ATMs, local tips, plan changes, and more!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [hasNew, setHasNew] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (open) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      setTimeout(() => inputRef.current?.focus(), 100);
      setHasNew(false);
    }
  }, [open, messages]);

  const sendMessage = async (text) => {
    const userText = (text || input).trim();
    if (!userText || loading) return;

    const userMsg = { role: "user", content: userText };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    // Build history (exclude first welcome message)
    const history = messages
      .slice(1)
      .map((m) => ({ role: m.role, content: m.content }));

    try {
      const data = await sendChatMessage(userText, history, tripContext);
      const aiMsg = { role: "assistant", content: data.reply };
      setMessages((prev) => [...prev, aiMsg]);
      if (!open) setHasNew(true);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I couldn't connect right now. Make sure the backend is running and try again! 🙏",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        role: "assistant",
        content: tripContext
          ? `Chat cleared! Still here for your **${tripContext.destination}** trip. What do you need? ✈️`
          : "Chat cleared! Ask me anything about your travel plans. ✈️",
      },
    ]);
  };

  // Format message text — bold **text**, line breaks
  const formatMsg = (text) => {
    return text
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br/>");
  };

  return (
    <>
      {/* Floating button */}
      <button
        className={`chatbot-fab ${open ? "chatbot-fab-open" : ""}`}
        onClick={() => setOpen((v) => !v)}
        aria-label="Open Travel Assistant"
      >
        {open ? "✕" : "🤖"}
        {hasNew && !open && <span className="chatbot-notif" />}
        {!open && <span className="chatbot-fab-label">Travel Assistant</span>}
      </button>

      {/* Chat window */}
      {open && (
        <div className="chatbot-window">
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-left">
              <div className="chatbot-avatar-ring">🤖</div>
              <div>
                <div className="chatbot-title">AI Travel Assistant</div>
                <div className="chatbot-subtitle">
                  {tripContext ? `📍 ${tripContext.destination} trip` : "Ask me anything"}
                </div>
              </div>
            </div>
            <div className="chatbot-header-actions">
              <button className="chatbot-clear-btn" onClick={clearChat} title="Clear chat">
                🗑️
              </button>
              <button className="chatbot-close-btn" onClick={() => setOpen(false)}>
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`chat-msg ${msg.role === "user" ? "chat-msg-user" : "chat-msg-ai"}`}
              >
                {msg.role === "assistant" && (
                  <div className="chat-avatar">🤖</div>
                )}
                <div
                  className={`chat-bubble ${msg.role === "user" ? "bubble-user" : "bubble-ai"}`}
                  dangerouslySetInnerHTML={{ __html: formatMsg(msg.content) }}
                />
                {msg.role === "user" && (
                  <div className="chat-avatar chat-avatar-user">👤</div>
                )}
              </div>
            ))}
            {loading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick prompts */}
          <div className="chatbot-quick-prompts">
            {QUICK_PROMPTS.slice(0, 4).map((q, i) => (
              <button
                key={i}
                className="quick-prompt-chip"
                onClick={() => sendMessage(q)}
                disabled={loading}
              >
                {q}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="chatbot-input-row">
            <textarea
              ref={inputRef}
              className="chatbot-input"
              placeholder="Ask anything about your trip..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              rows={1}
              disabled={loading}
            />
            <button
              className="chatbot-send-btn"
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              aria-label="Send"
            >
              {loading ? <span className="chat-spinner" /> : "➤"}
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default TravelChatbot;
