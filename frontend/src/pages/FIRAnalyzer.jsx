import { useState, useRef } from 'react';
import { firAPI } from '../api/client';
import {
  Upload, FileText, Send, AlertCircle, CheckCircle,
  Loader, ChevronDown, ChevronUp, FolderUp, Download, AlertTriangle, Copy
} from 'lucide-react';

export default function FIRAnalyzer() {
  const [mode, setMode] = useState('text'); // text | pdf | bulk
  const [narrative, setNarrative] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [bulkResult, setBulkResult] = useState(null);
  const [expandedSimilar, setExpandedSimilar] = useState(null);
  const [narrativeExpanded, setNarrativeExpanded] = useState(false);
  const fileInputRef = useRef(null);
  const bulkInputRef = useRef(null);

  const analyzeText = async () => {
    if (!narrative.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const { data } = await firAPI.analyzeText(narrative);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const uploadPDF = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const { data } = await firAPI.uploadPDF(file);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const bulkUpload = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    setLoading(true);
    setError('');
    setBulkResult(null);
    try {
      const isPDF = files[0].name.endsWith('.pdf');
      const { data } = isPDF
        ? await firAPI.bulkUploadPDF(files)
        : await firAPI.bulkUploadJSON(files);
      setBulkResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Bulk upload failed');
    } finally {
      setLoading(false);
    }
  };

  const downloadResult = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `FIR-analysis-${result.fir_number || 'result'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const SeverityBadge = ({ severity }) => (
    <span className={`badge badge-${severity || 'medium'}`}>
      {severity || 'N/A'}
    </span>
  );

  return (
    <>
      <h1 className="page-title">FIR Analyzer</h1>
      <p className="page-description">
        Analyze FIR narratives with AI — supports both Malayalam and English
      </p>

      {/* Mode Tabs */}
      <div className="tabs">
        <button className={`tab ${mode === 'text' ? 'active' : ''}`} onClick={() => setMode('text')}>
          Paste Narrative
        </button>
        <button className={`tab ${mode === 'pdf' ? 'active' : ''}`} onClick={() => setMode('pdf')}>
          Upload PDF
        </button>
        <button className={`tab ${mode === 'bulk' ? 'active' : ''}`} onClick={() => setMode('bulk')}>
          Bulk Upload
        </button>
      </div>

      <div className="grid-2">
        {/* Input Panel */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              {mode === 'text' && 'Enter FIR Narrative'}
              {mode === 'pdf' && 'Upload FIR PDF'}
              {mode === 'bulk' && 'Bulk Upload Previous FIRs'}
            </div>
          </div>

          {mode === 'text' && (
            <>
              <div className="form-group">
                <label className="form-label">FIR Narrative (Malayalam or English)</label>
                <textarea
                  className="form-textarea"
                  value={narrative}
                  onChange={(e) => setNarrative(e.target.value)}
                  placeholder={"Paste the FIR narrative here... \n\nSupports both Malayalam (e.g., 06.05.2024 തിയ്യതി രാത്രി...) and English narratives."}
                  style={{ minHeight: 220 }}
                />
              </div>
              <button
                className="btn btn-primary btn-lg"
                onClick={analyzeText}
                disabled={loading || !narrative.trim()}
                style={{ width: '100%' }}
              >
                {loading ? <><Loader size={18} className="spin" /> Analyzing...</> : <><Send size={18} /> Analyze Narrative</>}
              </button>
            </>
          )}

          {mode === 'pdf' && (
            <div
              className="upload-zone"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="upload-icon" size={48} />
              <div className="upload-text">Click to upload FIR PDF</div>
              <div className="upload-hint">The narrative will be extracted via OCR and analyzed</div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={uploadPDF}
                style={{ display: 'none' }}
              />
            </div>
          )}

          {mode === 'bulk' && (
            <>
              <div
                className="upload-zone"
                onClick={() => bulkInputRef.current?.click()}
                style={{ marginBottom: 16 }}
              >
                <FolderUp className="upload-icon" size={48} />
                <div className="upload-text">Upload multiple FIR files</div>
                <div className="upload-hint">
                  Accepts PDF files or pre-processed JSON files.
                  <br />All files will be processed, analyzed, and stored in the database.
                  <br /><strong>Duplicates are automatically detected and skipped.</strong>
                </div>
                <input
                  ref={bulkInputRef}
                  type="file"
                  accept=".pdf,.json"
                  multiple
                  onChange={bulkUpload}
                  style={{ display: 'none' }}
                />
              </div>

              {bulkResult && (
                <div className="card" style={{ background: 'var(--bg-tertiary)', marginTop: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                    <CheckCircle size={20} color="var(--accent-emerald)" />
                    <span style={{ fontWeight: 600 }}>Bulk Upload Complete</span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 12 }}>
                    <div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{bulkResult.total_files}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Total Files</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>{bulkResult.processed}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Processed</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--accent-amber, #f59e0b)' }}>{bulkResult.skipped_duplicates || 0}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Duplicates</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--accent-red)' }}>{bulkResult.failed}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Failed</div>
                    </div>
                  </div>

                  {/* Duplicate list */}
                  {bulkResult.duplicates?.length > 0 && (
                    <div style={{ marginTop: 12, padding: 10, background: 'rgba(245, 158, 11, 0.08)', borderRadius: 8, border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6, fontSize: '0.82rem', fontWeight: 600, color: 'var(--accent-amber, #f59e0b)' }}>
                        <AlertTriangle size={14} /> Duplicates Skipped
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                        {bulkResult.duplicates.map((d, i) => <div key={i}>• {d}</div>)}
                      </div>
                    </div>
                  )}

                  {bulkResult.errors?.length > 0 && (
                    <div style={{ marginTop: 12, fontSize: '0.8rem', color: 'var(--accent-red)' }}>
                      {bulkResult.errors.map((e, i) => <div key={i}>• {e}</div>)}
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {loading && (
            <div className="loading-overlay" style={{ padding: 24 }}>
              <div className="spinner" />
              <span>Processing FIR narrative...</span>
            </div>
          )}

          {error && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12, color: 'var(--accent-red)', fontSize: '0.85rem' }}>
              <AlertCircle size={16} /> {error}
            </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Analysis Results</div>
            {result && (
              <button className="btn btn-ghost btn-sm" onClick={downloadResult} title="Download analysis as JSON">
                <Download size={14} /> Download
              </button>
            )}
          </div>

          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>

              {/* Duplicate Warning */}
              {result.is_duplicate && (
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 10, padding: 12,
                  background: 'rgba(245, 158, 11, 0.1)', borderRadius: 8,
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  fontSize: '0.85rem', color: 'var(--accent-amber, #f59e0b)',
                }}>
                  <AlertTriangle size={18} />
                  <div>
                    <strong>Duplicate Detected</strong> — This FIR already exists in the database
                    {result.duplicate_of_id && <span> (FIR #{result.duplicate_of_id})</span>}.
                    It was not added again.
                  </div>
                </div>
              )}

              {/* Classification */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Crime Type</div>
                  <span className="badge badge-blue" style={{ fontSize: '0.82rem' }}>
                    {(result.crime_type || 'Unknown').replace(/_/g, ' ')}
                  </span>
                </div>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Severity</div>
                  <SeverityBadge severity={result.severity} />
                </div>
              </div>

              {/* FIR Number */}
              {result.fir_number && (
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>FIR Number</div>
                  <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>{result.fir_number}</span>
                </div>
              )}

              {/* Extracted Narrative */}
              {result.narrative && (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                      Extracted Narrative
                    </div>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => setNarrativeExpanded(!narrativeExpanded)}
                      style={{ fontSize: '0.72rem' }}
                    >
                      {narrativeExpanded ? <><ChevronUp size={12} /> Collapse</> : <><ChevronDown size={12} /> Expand</>}
                    </button>
                  </div>
                  <div
                    className="narrative-box"
                    style={{
                      maxHeight: narrativeExpanded ? 'none' : 120,
                      overflow: narrativeExpanded ? 'visible' : 'hidden',
                      position: 'relative',
                    }}
                  >
                    {result.narrative}
                    {!narrativeExpanded && result.narrative.length > 300 && (
                      <div style={{
                        position: 'absolute', bottom: 0, left: 0, right: 0, height: 40,
                        background: 'linear-gradient(transparent, var(--bg-card))',
                      }} />
                    )}
                  </div>
                </div>
              )}

              {/* English Summary */}
              {result.summary_en && (
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>English Summary</div>
                  <div className="narrative-box">{result.summary_en}</div>
                </div>
              )}

              {/* IPC Sections */}
              {result.ipc_sections?.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Applicable Sections</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {result.ipc_sections.map((s, i) => (
                      <div key={i} className="badge badge-purple" title={s.description}>
                        {s.act} §{s.section}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommended Steps */}
              {result.recommended_steps?.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Recommended Investigation Steps</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {result.recommended_steps.map((step, i) => (
                      <div key={i} style={{ display: 'flex', gap: 10, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        <span style={{ color: 'var(--accent-blue)', fontWeight: 700, minWidth: 18 }}>{i + 1}.</span>
                        {step}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Similar FIRs */}
              {result.similar_firs?.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Similar Cases</div>
                  {result.similar_firs.map((sim, i) => (
                    <div key={i} className="fir-card" style={{ marginBottom: 8, cursor: 'pointer' }}
                         onClick={() => setExpandedSimilar(expandedSimilar === i ? null : i)}>
                      <div className="fir-header">
                        <span className="fir-id">#{sim.id} {sim.file_name || ''}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div className="similarity-bar">
                            <div className="fill" style={{ width: `${sim.similarity_score * 100}%` }} />
                          </div>
                          <span style={{ fontSize: '0.78rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                            {(sim.similarity_score * 100).toFixed(1)}%
                          </span>
                          {expandedSimilar === i ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        </div>
                      </div>
                      {expandedSimilar === i && sim.narrative && (
                        <div className="narrative-box" style={{ marginTop: 8, maxHeight: 150 }}>
                          {sim.narrative}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: 48 }}>
              <FileText className="empty-icon" size={48} />
              <div className="empty-title">No Analysis Yet</div>
              <div className="empty-text">Paste a narrative or upload a FIR PDF to see AI analysis</div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
