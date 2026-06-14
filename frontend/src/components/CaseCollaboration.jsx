import { useState, useEffect, useCallback } from 'react';
import { MessageSquare, Clock, Trash2, Edit2, Send, X, Check } from 'lucide-react';
import { casesAPI } from '../api/client';

const EVENT_LABELS = {
  created: 'FIR registered',
  status_changed: 'Status changed',
  note_added: 'Note added',
  analyzed: 'Analyzed',
  similar_found: 'Similar cases found',
  pattern_matched: 'Pattern matched',
  tagged: 'Tag updated',
  bulk_updated: 'Bulk update',
};

function timeAgo(ts) {
  if (!ts) return '';
  const diff = (Date.now() - new Date(ts).getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return new Date(ts).toLocaleDateString();
}

export default function CaseCollaboration({ firId }) {
  const [tab, setTab] = useState('notes');
  const [notes, setNotes] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const loadNotes = useCallback(async () => {
    try {
      const { data } = await casesAPI.listNotes(firId);
      setNotes(data);
    } catch { setNotes([]); }
  }, [firId]);

  const loadTimeline = useCallback(async () => {
    try {
      const { data } = await casesAPI.getTimeline(firId);
      setTimeline(data);
    } catch { setTimeline([]); }
  }, [firId]);

  useEffect(() => {
    setLoading(true);
    Promise.all([loadNotes(), loadTimeline()]).finally(() => setLoading(false));
  }, [loadNotes, loadTimeline]);

  const addNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim()) return;
    setSaving(true);
    try {
      await casesAPI.addNote(firId, newNote.trim());
      setNewNote('');
      await Promise.all([loadNotes(), loadTimeline()]);
    } catch { /* ignore */ } finally { setSaving(false); }
  };

  const saveEdit = async (id) => {
    if (!editText.trim()) return;
    try {
      await casesAPI.updateNote(id, editText.trim());
      setEditingId(null);
      setEditText('');
      await loadNotes();
    } catch { /* ignore */ }
  };

  const removeNote = async (id) => {
    try {
      await casesAPI.deleteNote(id);
      await Promise.all([loadNotes(), loadTimeline()]);
    } catch { /* ignore */ }
  };

  const tabBtn = (key, label, Icon) => (
    <button
      onClick={() => setTab(key)}
      className="btn btn-ghost btn-sm"
      style={{
        display: 'flex', gap: 5, alignItems: 'center',
        borderBottom: tab === key ? '2px solid var(--accent-blue, #3b82f6)' : '2px solid transparent',
        borderRadius: 0, color: tab === key ? 'var(--accent-blue, #3b82f6)' : 'var(--text-muted)',
        fontWeight: tab === key ? 600 : 400,
      }}
    >
      <Icon size={14} /> {label}
    </button>
  );

  return (
    <div style={{ marginTop: 18, borderTop: '1px solid var(--border, #233)', paddingTop: 14 }}>
      <div style={{ display: 'flex', gap: 4, marginBottom: 12 }}>
        {tabBtn('notes', `Notes${notes.length ? ` (${notes.length})` : ''}`, MessageSquare)}
        {tabBtn('timeline', 'Timeline', Clock)}
      </div>

      {loading ? (
        <div className="loading-overlay" style={{ padding: 16 }}><div className="spinner" style={{ width: 20, height: 20 }} /></div>
      ) : tab === 'notes' ? (
        <div>
          <form onSubmit={addNote} style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            <input
              className="form-input"
              style={{ flex: 1 }}
              placeholder="Add a case note..."
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              maxLength={5000}
            />
            <button type="submit" className="btn btn-primary btn-sm" disabled={saving || !newNote.trim()}>
              <Send size={14} />
            </button>
          </form>

          {notes.length === 0 ? (
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>No notes yet. Add the first one.</div>
          ) : (
            notes.map((n) => (
              <div key={n.id} style={{
                padding: '10px 12px', marginBottom: 8, borderRadius: 8,
                background: 'var(--bg-input, rgba(255,255,255,0.03))',
              }}>
                {editingId === n.id ? (
                  <div style={{ display: 'flex', gap: 6 }}>
                    <input className="form-input" style={{ flex: 1 }} value={editText}
                      onChange={(e) => setEditText(e.target.value)} maxLength={5000} />
                    <button className="btn btn-primary btn-sm" onClick={() => saveEdit(n.id)}><Check size={13} /></button>
                    <button className="btn btn-ghost btn-sm" onClick={() => { setEditingId(null); setEditText(''); }}><X size={13} /></button>
                  </div>
                ) : (
                  <>
                    <div style={{ fontSize: '0.84rem', color: 'var(--text-primary, #e6e9ef)', whiteSpace: 'pre-wrap' }}>{n.text}</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                        {n.author_name || 'Unknown'} · {timeAgo(n.created_at)}
                        {n.updated_at && n.updated_at !== n.created_at ? ' (edited)' : ''}
                      </span>
                      {n.can_edit && (
                        <span style={{ display: 'flex', gap: 4 }}>
                          <button className="btn btn-ghost btn-sm" style={{ padding: 3 }}
                            onClick={() => { setEditingId(n.id); setEditText(n.text); }} title="Edit">
                            <Edit2 size={12} />
                          </button>
                          <button className="btn btn-ghost btn-sm" style={{ padding: 3 }}
                            onClick={() => removeNote(n.id)} title="Delete">
                            <Trash2 size={12} />
                          </button>
                        </span>
                      )}
                    </div>
                  </>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        <div style={{ position: 'relative', paddingLeft: 16 }}>
          {timeline.length === 0 ? (
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>No events recorded.</div>
          ) : (
            timeline.map((ev, i) => (
              <div key={ev.id || i} style={{ position: 'relative', paddingBottom: 16 }}>
                {/* connector line */}
                {i < timeline.length - 1 && (
                  <span style={{ position: 'absolute', left: -10, top: 14, bottom: 0, width: 2, background: 'var(--border, #233)' }} />
                )}
                {/* dot */}
                <span style={{
                  position: 'absolute', left: -14, top: 4, width: 10, height: 10, borderRadius: '50%',
                  background: 'var(--accent-blue, #3b82f6)', border: '2px solid var(--bg-card, #131a2a)',
                }} />
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary, #e6e9ef)' }}>
                  {EVENT_LABELS[ev.event_type] || ev.event_type}
                </div>
                {ev.description && (
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary, #aab)', marginTop: 1 }}>{ev.description}</div>
                )}
                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 2 }}>{timeAgo(ev.created_at)}</div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
