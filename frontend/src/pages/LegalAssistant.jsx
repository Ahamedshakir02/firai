import { useState, useRef, useEffect } from 'react';
import { legalAPI } from '../api/client';
import { Send, Scale, BookOpen, Loader, Bot, User, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LegalAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content: 'Welcome! I am your AI Legal Assistant for Kerala Police.\n\nI can help you with:\n• IPC/BNS section guidance\n• Legal procedure clarification\n• Bail eligibility queries\n• Court precedent insights\n• Investigation procedure guidance\n\nAsk me any legal question related to your FIR investigation.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sections, setSections] = useState([]);
  const [showSections, setShowSections] = useState(false);
  const messagesEnd = useRef(null);
  const { officer } = useAuth();

  const clearChat = () => {
    setMessages([{
      role: 'ai',
      content: 'Chat cleared. How can I help you with your investigation?',
    }]);
  };

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const { data } = await legalAPI.query(input);
      const aiMsg = {
        role: 'ai',
        content: data.answer,
        sections: data.relevant_sections,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: 'Sorry, I encountered an error processing your question. Please check the backend connection and try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadSections = async () => {
    try {
      const { data } = await legalAPI.getSections();
      setSections(data);
      setShowSections(!showSections);
    } catch (err) {
      console.error(err);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <h1 className="page-title">Legal Assistant</h1>
      <p className="page-description">AI-powered legal guidance — ask about IPC, BNS, CrPC procedures and sections</p>

      <div className="grid-2">
        {/* Chat Panel */}
        <div className="card" style={{ padding: 0, display: 'flex', flexDirection: 'column', height: 'calc(100vh - 200px)' }}>
          <div className="card-header" style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <Scale size={20} color="var(--accent-gold)" />
              <div className="card-title">Legal Chat</div>
              {officer && (
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>
                  {officer.name}
                </span>
              )}
            </div>
            <button className="btn btn-ghost btn-sm" onClick={clearChat} title="Clear chat history">
              <Trash2 size={14} /> Clear
            </button>
          </div>

          <div className="chat-messages" style={{ flex: 1 }}>
            {messages.map((msg, i) => (
              <div key={i}>
                <div className={`chat-bubble ${msg.role}`}>
                  <div style={{ display: 'flex', gap: 8, marginBottom: 6, alignItems: 'center' }}>
                    {msg.role === 'ai' ? (
                      <Bot size={14} color="var(--accent-blue)" />
                    ) : (
                      <User size={14} />
                    )}
                    <span style={{ fontSize: '0.72rem', fontWeight: 600, opacity: 0.7 }}>
                      {msg.role === 'ai' ? 'AI Legal Assistant' : (officer?.name || 'You')}
                    </span>
                  </div>
                  <div style={{ whiteSpace: 'pre-line' }}>{msg.content}</div>
                </div>
                {msg.sections?.length > 0 && (
                  <div style={{ marginLeft: 16, marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {msg.sections.map((s, j) => (
                      <div key={j} className="badge badge-purple" title={s.description}>
                        {s.act} §{s.section}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="chat-bubble ai" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Loader size={16} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
                Analyzing legal query...
              </div>
            )}
            <div ref={messagesEnd} />
          </div>

          <div className="chat-input-area">
            <input
              type="text"
              placeholder="Ask a legal question... (e.g., 'What is the bail status for IPC 324?')"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button className="btn btn-primary" onClick={sendMessage} disabled={loading || !input.trim()}>
              <Send size={16} />
            </button>
          </div>
        </div>

        {/* Reference Panel */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <BookOpen size={20} color="var(--accent-cyan)" />
              <div className="card-title">Legal Reference</div>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={loadSections}>
              {showSections ? 'Hide' : 'Show'} IPC/BNS Sections
            </button>
          </div>

          {/* Quick Reference */}
          <div style={{ marginBottom: 18 }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase' }}>
              Common Questions
            </div>
            {[
              'What is the punishment for IPC Section 324?',
              'Is BNS Section 329(4) bailable?',
              'What are the investigation steps for a cheating case?',
              'Difference between IPC 323 and 324?',
              'What is the bail procedure for assault cases in Kerala?',
            ].map((q, i) => (
              <div
                key={i}
                onClick={() => setInput(q)}
                style={{
                  padding: '10px 14px', marginBottom: 6, background: 'var(--bg-tertiary)',
                  borderRadius: 'var(--radius-md)', fontSize: '0.83rem', color: 'var(--text-secondary)',
                  cursor: 'pointer', transition: 'all 0.15s ease',
                  border: '1px solid var(--border-color)',
                }}
                onMouseEnter={(e) => e.target.style.borderColor = 'var(--accent-blue)'}
                onMouseLeave={(e) => e.target.style.borderColor = 'var(--border-color)'}
              >
                {q}
              </div>
            ))}
          </div>

          {/* Sections Table */}
          {showSections && sections.length > 0 && (
            <div style={{ maxHeight: 400, overflowY: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Act</th>
                    <th>Section</th>
                    <th>Description</th>
                    <th>Bailable</th>
                  </tr>
                </thead>
                <tbody>
                  {sections.map((s, i) => (
                    <tr key={i}>
                      <td style={{ fontSize: '0.75rem' }}>{s.act}</td>
                      <td style={{ fontWeight: 600, color: 'var(--accent-blue-light)' }}>{s.section}</td>
                      <td style={{ fontSize: '0.78rem' }}>{s.description}</td>
                      <td>
                        <span className={`badge ${s.bailable ? 'badge-low' : 'badge-critical'}`}>
                          {s.bailable ? 'Yes' : 'No'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
