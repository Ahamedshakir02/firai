import { useState } from 'react';
import { translateAPI } from '../api/client';
import { Languages, ArrowRightLeft, Loader, Copy, CheckCircle } from 'lucide-react';

export default function Translation() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [sourceLang, setSourceLang] = useState('ml');
  const [targetLang, setTargetLang] = useState('en');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [engine, setEngine] = useState(null); // 'bhashini', 'google', or 'none'

  const translate = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setEngine(null);
    try {
      const { data } = await translateAPI.translate(inputText, sourceLang, targetLang);
      setOutputText(data.translated_text);
      setEngine(data.engine || null);
    } catch (err) {
      setOutputText('Translation failed. Please try again later.');
      setEngine(null);
    } finally {
      setLoading(false);
    }
  };

  const swapLanguages = () => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    setInputText(outputText);
    setOutputText(inputText);
    setEngine(null);
  };

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(outputText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const langNames = { ml: 'Malayalam', en: 'English', hi: 'Hindi' };

  const engineLabels = {
    bhashini: { label: 'Bhashini API', color: 'var(--accent-emerald)' },
    google:   { label: 'Google Translate (fallback)', color: 'var(--accent-amber, #f59e0b)' },
    none:     { label: 'No translation engine available', color: 'var(--accent-red, #ef4444)' },
  };

  return (
    <>
      <h1 className="page-title">Translation</h1>
      <p className="page-description">
        Translate FIR narratives between Malayalam and English — powered by Bhashini API with Google Translate fallback
      </p>

      {/* Language Selector */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 20 }}>
          <select
            className="form-select"
            style={{ width: 200, textAlign: 'center' }}
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value)}
          >
            <option value="ml">🇮🇳 Malayalam</option>
            <option value="en">🇬🇧 English</option>
            <option value="hi">🇮🇳 Hindi</option>
          </select>

          <button
            className="btn btn-ghost"
            onClick={swapLanguages}
            style={{ padding: 10, borderRadius: '50%' }}
          >
            <ArrowRightLeft size={20} />
          </button>

          <select
            className="form-select"
            style={{ width: 200, textAlign: 'center' }}
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
          >
            <option value="en">🇬🇧 English</option>
            <option value="ml">🇮🇳 Malayalam</option>
            <option value="hi">🇮🇳 Hindi</option>
          </select>
        </div>
      </div>

      {/* Translation Panels */}
      <div className="grid-2">
        {/* Input */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">{langNames[sourceLang]} Input</div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              {inputText.length} characters
            </span>
          </div>
          <textarea
            className="form-textarea"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={sourceLang === 'ml'
              ? 'ഇവിടെ മലയാളം ടെക്സ്റ്റ് പേസ്റ്റ് ചെയ്യുക...'
              : 'Paste English text here... (e.g., FIR narrative)'}
            style={{ minHeight: 260 }}
          />
          <button
            className="btn btn-primary btn-lg"
            onClick={translate}
            disabled={loading || !inputText.trim()}
            style={{ width: '100%', marginTop: 14 }}
          >
            {loading ? (
              <><Loader size={18} style={{ animation: 'spin 1s linear infinite' }} /> Translating...</>
            ) : (
              <><Languages size={18} /> Translate</>
            )}
          </button>
        </div>

        {/* Output */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">{langNames[targetLang]} Output</div>
            {outputText && (
              <button className="btn btn-ghost btn-sm" onClick={copyToClipboard}>
                {copied ? <><CheckCircle size={14} color="var(--accent-emerald)" /> Copied</> : <><Copy size={14} /> Copy</>}
              </button>
            )}
          </div>

          {outputText ? (
            <>
              <div className="narrative-box" style={{ minHeight: 260 }}>
                {outputText}
              </div>

              {/* Engine badge */}
              {engine && (
                <div style={{
                  marginTop: 10,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontSize: '0.78rem',
                }}>
                  <span style={{
                    display: 'inline-block',
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: engineLabels[engine]?.color || 'var(--text-muted)',
                  }} />
                  <span style={{ color: 'var(--text-muted)' }}>
                    Translated via: <strong style={{ color: engineLabels[engine]?.color }}>
                      {engineLabels[engine]?.label || engine}
                    </strong>
                  </span>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state" style={{ minHeight: 260 }}>
              <Languages className="empty-icon" size={48} />
              <div className="empty-title">Translation Output</div>
              <div className="empty-text">Enter text and click Translate to see results</div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
