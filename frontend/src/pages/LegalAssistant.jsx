import { useState, useRef, useEffect } from 'react';
import { legalAPI } from '../api/client';
import { Send, Scale, BookOpen, Loader, Bot, User, Trash2, ArrowRightLeft, Calculator, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LegalAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content: 'Welcome! I am your AI Legal Assistant for Kerala Police.\n\nI can help you with:\n• IPC/BNS section guidance (try "IPC 302" or "BNS 103")\n• Legal procedure clarification\n• Bail eligibility queries (try "Is 420 bailable?")\n• IPC ↔ BNS cross-mapping\n• Punishment calculation\n• Investigation procedure guidance\n\nAsk me any legal question related to your FIR investigation.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sections, setSections] = useState([]);
  const [showSections, setShowSections] = useState(false);
  const messagesEnd = useRef(null);
  const { officer } = useAuth();

  // Punishment Calculator state
  const [calcSections, setCalcSections] = useState([{ act: 'IPC', section: '' }]);
  const [calcResult, setCalcResult] = useState(null);
  const [calcLoading, setCalcLoading] = useState(false);

  // IPC↔BNS Mapper state
  const [mapperAct, setMapperAct] = useState('IPC');
  const [mapperSection, setMapperSection] = useState('');
  const [mapperResult, setMapperResult] = useState(null);
  const [mapperLoading, setMapperLoading] = useState(false);

  // Active panel
  const [activePanel, setActivePanel] = useState('reference');

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

  // ── IPC↔BNS Mapper ──
  const lookupEquivalent = async () => {
    if (!mapperSection.trim()) return;
    setMapperLoading(true);
    try {
      const { data } = await legalAPI.getEquivalent(mapperAct, mapperSection.trim());
      setMapperResult(data);
    } catch (err) {
      setMapperResult({ found: false, error: 'Lookup failed' });
    } finally {
      setMapperLoading(false);
    }
  };

  // ── Punishment Calculator ──
  const addCalcSection = () => {
    setCalcSections((prev) => [...prev, { act: 'IPC', section: '' }]);
  };

  const removeCalcSection = (idx) => {
    setCalcSections((prev) => prev.filter((_, i) => i !== idx));
  };

  const updateCalcSection = (idx, field, value) => {
    setCalcSections((prev) => prev.map((s, i) => i === idx ? { ...s, [field]: value } : s));
  };

  const calculatePunishment = async () => {
    const valid = calcSections.filter((s) => s.section.trim());
    if (!valid.length) return;
    setCalcLoading(true);
    try {
      const { data } = await legalAPI.calcPunishment(valid);
      setCalcResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setCalcLoading(false);
    }
  };

  // ── Render markdown-like bold ──
  const renderText = (text) => {
    if (!text) return '';
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <>
      <h1 className="page-title">Legal Assistant</h1>
      <p className="page-description">AI-powered legal guidance — IPC/BNS search, section mapping, and punishment calculator</p>

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
                  <div style={{ whiteSpace: 'pre-line' }}>{renderText(msg.content)}</div>
                </div>
                {msg.sections?.length > 0 && (
                  <div style={{ marginLeft: 16, marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {msg.sections.map((s, j) => (
                      <div key={j} className="badge badge-purple" title={s.description}
                        style={{ cursor: 'pointer' }}
                        onClick={() => setInput(`${s.act} ${s.section}`)}>
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
              placeholder="Ask a legal question... (e.g., 'IPC 302', 'Is 420 bailable?', 'acid attack')"
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

        {/* Right Panel — Tabs */}
        <div className="card">
          {/* Panel Tabs */}
          <div style={{ display: 'flex', gap: 4, marginBottom: 16, borderBottom: '1px solid var(--border-color)', paddingBottom: 12 }}>
            {[
              { id: 'reference', label: 'Reference', icon: BookOpen },
              { id: 'mapper', label: 'IPC↔BNS', icon: ArrowRightLeft },
              { id: 'calculator', label: 'Punishment', icon: Calculator },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                className={`btn btn-sm ${activePanel === id ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setActivePanel(id)}
                style={{ flex: 1, gap: 6 }}
              >
                <Icon size={14} /> {label}
              </button>
            ))}
          </div>

          {/* ── Reference Panel ── */}
          {activePanel === 'reference' && (
            <>
              <div className="card-header" style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <BookOpen size={20} color="var(--accent-cyan)" />
                  <div className="card-title">Legal Reference</div>
                </div>
                <button className="btn btn-secondary btn-sm" onClick={loadSections}>
                  {showSections ? 'Hide' : 'Show'} Sections
                </button>
              </div>

              <div style={{ marginBottom: 18 }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase' }}>
                  Common Questions
                </div>
                {[
                  'What is the punishment for IPC Section 324?',
                  'Is BNS Section 329(4) bailable?',
                  'What are the investigation steps for a cheating case?',
                  'What to do when acid is thrown at someone?',
                  'Kidnapping bail and punishment details',
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
            </>
          )}

          {/* ── IPC ↔ BNS Mapper Panel ── */}
          {activePanel === 'mapper' && (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                <ArrowRightLeft size={20} color="var(--accent-gold)" />
                <div className="card-title">IPC ↔ BNS Cross-Mapping</div>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 16 }}>
                Find the equivalent section when converting between IPC (old) and BNS (new) codes.
              </p>

              <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                <select
                  value={mapperAct}
                  onChange={(e) => setMapperAct(e.target.value)}
                  style={{
                    padding: '8px 12px', background: 'var(--bg-tertiary)', color: 'var(--text-primary)',
                    border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)',
                    fontSize: '0.85rem',
                  }}
                >
                  <option value="IPC">IPC →</option>
                  <option value="BNS">BNS →</option>
                </select>
                <input
                  type="text"
                  placeholder="Section (e.g. 302)"
                  value={mapperSection}
                  onChange={(e) => setMapperSection(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && lookupEquivalent()}
                  style={{ flex: 1 }}
                />
                <button className="btn btn-primary btn-sm" onClick={lookupEquivalent}
                  disabled={mapperLoading || !mapperSection.trim()}>
                  {mapperLoading ? <Loader size={14} style={{ animation: 'spin 1s linear infinite' }} /> : 'Map'}
                </button>
              </div>

              {mapperResult && (
                <div style={{
                  padding: 16, borderRadius: 'var(--radius-md)',
                  background: mapperResult.found ? 'rgba(34, 197, 94, 0.08)' : 'rgba(239, 68, 68, 0.08)',
                  border: `1px solid ${mapperResult.found ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                }}>
                  {mapperResult.found ? (
                    <>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                        <div className="badge badge-purple">{mapperResult.source_act} §{mapperResult.source_section}</div>
                        <ArrowRightLeft size={16} color="var(--accent-gold)" />
                        <div className="badge badge-blue">{mapperResult.equivalent_act} §{mapperResult.equivalent_section}</div>
                      </div>
                      {mapperResult.equivalent_details && (
                        <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                          <strong>{mapperResult.equivalent_details.description}</strong>
                          {mapperResult.equivalent_details.punishment && (
                            <div style={{ marginTop: 6 }}>
                              Punishment: {mapperResult.equivalent_details.punishment}
                            </div>
                          )}
                          <div style={{ marginTop: 6, display: 'flex', gap: 8 }}>
                            <span className={`badge ${mapperResult.equivalent_details.bailable ? 'badge-low' : 'badge-critical'}`}>
                              {mapperResult.equivalent_details.bailable ? 'Bailable' : 'Non-Bailable'}
                            </span>
                            <span className={`badge ${mapperResult.equivalent_details.cognizable ? 'badge-medium' : 'badge-low'}`}>
                              {mapperResult.equivalent_details.cognizable ? 'Cognizable' : 'Non-Cognizable'}
                            </span>
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      No equivalent found for {mapperAct} Section {mapperSection}
                    </div>
                  )}
                </div>
              )}

              {/* Quick mapping examples */}
              <div style={{ marginTop: 20, fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
                Common Mappings
              </div>
              {[
                { ipc: '302', bns: '103', desc: 'Murder' },
                { ipc: '420', bns: '318(4)', desc: 'Cheating' },
                { ipc: '376', bns: '64', desc: 'Rape' },
                { ipc: '498A', bns: '85', desc: 'Domestic Cruelty' },
                { ipc: '307', bns: '109', desc: 'Attempt to Murder' },
              ].map((m, i) => (
                <div key={i}
                  onClick={() => { setMapperAct('IPC'); setMapperSection(m.ipc); }}
                  style={{
                    padding: '8px 12px', marginBottom: 4, background: 'var(--bg-tertiary)',
                    borderRadius: 'var(--radius-md)', fontSize: '0.8rem', cursor: 'pointer',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    border: '1px solid var(--border-color)',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--accent-gold)'}
                  onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
                >
                  <span>{m.desc}</span>
                  <span style={{ color: 'var(--text-muted)' }}>IPC {m.ipc} → BNS {m.bns}</span>
                </div>
              ))}
            </>
          )}

          {/* ── Punishment Calculator Panel ── */}
          {activePanel === 'calculator' && (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                <Calculator size={20} color="var(--accent-cyan)" />
                <div className="card-title">Punishment Calculator</div>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 16 }}>
                Enter sections to see punishment, bail status, and severity breakdown.
              </p>

              {calcSections.map((cs, idx) => (
                <div key={idx} style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
                  <select
                    value={cs.act}
                    onChange={(e) => updateCalcSection(idx, 'act', e.target.value)}
                    style={{
                      padding: '8px 12px', background: 'var(--bg-tertiary)', color: 'var(--text-primary)',
                      border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)',
                      fontSize: '0.85rem', width: 90,
                    }}
                  >
                    <option value="IPC">IPC</option>
                    <option value="BNS">BNS</option>
                    <option value="NDPS Act">NDPS</option>
                    <option value="IT Act">IT Act</option>
                    <option value="POCSO Act">POCSO</option>
                    <option value="Arms Act">Arms</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Section"
                    value={cs.section}
                    onChange={(e) => updateCalcSection(idx, 'section', e.target.value)}
                    style={{ flex: 1 }}
                  />
                  {calcSections.length > 1 && (
                    <button className="btn btn-ghost btn-sm" onClick={() => removeCalcSection(idx)}>✕</button>
                  )}
                </div>
              ))}

              <div style={{ display: 'flex', gap: 8, marginTop: 8, marginBottom: 16 }}>
                <button className="btn btn-ghost btn-sm" onClick={addCalcSection}>+ Add Section</button>
                <button className="btn btn-primary btn-sm" onClick={calculatePunishment}
                  disabled={calcLoading || !calcSections.some((s) => s.section.trim())}
                  style={{ marginLeft: 'auto' }}>
                  {calcLoading ? <Loader size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <><Shield size={14} /> Calculate</>}
                </button>
              </div>

              {calcResult && (
                <div>
                  {/* Summary */}
                  <div style={{
                    padding: 14, marginBottom: 14, borderRadius: 'var(--radius-md)',
                    background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)',
                  }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
                      Overall Assessment
                    </div>
                    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                      <span className={`badge badge-${calcResult.summary.overall_severity}`}>
                        Severity: {calcResult.summary.overall_severity?.toUpperCase()}
                      </span>
                      <span className={`badge ${calcResult.summary.any_non_bailable ? 'badge-critical' : 'badge-low'}`}>
                        {calcResult.summary.any_non_bailable ? 'Non-Bailable Offence' : 'All Bailable'}
                      </span>
                      <span className="badge badge-medium">
                        {calcResult.summary.sections_found}/{calcResult.summary.total_sections} found
                      </span>
                    </div>
                  </div>

                  {/* Per-section results */}
                  <div style={{ maxHeight: 350, overflowY: 'auto' }}>
                    {calcResult.sections.map((s, i) => (
                      <div key={i} style={{
                        padding: 12, marginBottom: 8, borderRadius: 'var(--radius-md)',
                        background: s.found ? 'var(--bg-secondary)' : 'rgba(239, 68, 68, 0.05)',
                        border: `1px solid ${s.found ? 'var(--border-color)' : 'rgba(239, 68, 68, 0.2)'}`,
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                          <strong style={{ fontSize: '0.85rem' }}>{s.act} §{s.section}</strong>
                          <span className={`badge badge-${s.severity || 'medium'}`}>{s.severity}</span>
                        </div>
                        {s.found ? (
                          <>
                            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 6 }}>{s.title}</div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                              <strong>Punishment:</strong> {s.punishment}
                            </div>
                            <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                              <span className={`badge ${s.bailable ? 'badge-low' : 'badge-critical'}`} style={{ fontSize: '0.7rem' }}>
                                {s.bailable ? 'Bailable ✅' : 'Non-Bailable ❌'}
                              </span>
                              <span className={`badge ${s.cognizable ? 'badge-medium' : 'badge-low'}`} style={{ fontSize: '0.7rem' }}>
                                {s.cognizable ? 'Cognizable' : 'Non-Cognizable'}
                              </span>
                            </div>
                          </>
                        ) : (
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Section not found in knowledge base</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
}
