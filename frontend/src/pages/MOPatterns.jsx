import { useState, useEffect } from 'react';
import { moAPI } from '../api/client';
import { Fingerprint, RefreshCw, AlertTriangle, Link2, Loader } from 'lucide-react';

export default function MOPatterns() {
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);

  useEffect(() => { loadPatterns(); }, []);

  const loadPatterns = async () => {
    try {
      const { data } = await moAPI.getPatterns();
      setPatterns(data);
    } catch (err) {
      console.error('Failed to load patterns:', err);
    } finally {
      setLoading(false);
    }
  };

  const runDetection = async () => {
    setDetecting(true);
    try {
      const { data } = await moAPI.detect();
      setPatterns(data);
    } catch (err) {
      console.error('Detection failed:', err);
    } finally {
      setDetecting(false);
    }
  };

  return (
    <>
      <h1 className="page-title">MO Pattern Detection</h1>
      <p className="page-description">
        Detect recurring Modus Operandi patterns across FIR narratives
      </p>

      <div style={{ marginBottom: 24, display: 'flex', gap: 12 }}>
        <button className="btn btn-primary" onClick={runDetection} disabled={detecting}>
          {detecting ? (
            <><Loader size={16} style={{ animation: 'spin 1s linear infinite' }} /> Detecting Patterns...</>
          ) : (
            <><RefreshCw size={16} /> Run MO Detection</>
          )}
        </button>
      </div>

      {loading ? (
        <div className="loading-overlay"><div className="spinner" /><span>Loading patterns...</span></div>
      ) : patterns.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <Fingerprint className="empty-icon" size={64} />
            <div className="empty-title">No Patterns Detected Yet</div>
            <div className="empty-text">
              Click "Run MO Detection" to analyze all FIR narratives for recurring crime patterns
            </div>
          </div>
        </div>
      ) : (
        <div className="grid-2">
          {patterns.map((pattern) => (
            <div key={pattern.id} className="card" style={{ borderLeftWidth: 4, borderLeftColor: 'var(--accent-gold)' }}>
              <div className="card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <AlertTriangle size={18} color="var(--accent-gold)" />
                  <div className="card-title">{pattern.pattern_name}</div>
                </div>
                <span className="badge badge-gold">{pattern.occurrence_count} cases</span>
              </div>

              {pattern.description && (
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 14 }}>
                  {pattern.description}
                </p>
              )}

              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
                {pattern.crime_type && (
                  <span className="badge badge-blue">{pattern.crime_type.replace(/_/g, ' ')}</span>
                )}
                {pattern.linked_fir_ids?.length > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <Link2 size={12} />
                    Linked FIRs: {pattern.linked_fir_ids.map(id => `#${id}`).join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
