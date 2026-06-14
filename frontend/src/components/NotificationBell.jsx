import { useState, useEffect, useRef, useCallback } from 'react';
import { Bell, Check, CheckCheck } from 'lucide-react';
import { casesAPI } from '../api/client';

const POLL_MS = 60000; // refresh unread count every minute

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(false);
  const ref = useRef(null);

  const refreshCount = useCallback(async () => {
    try {
      const { data } = await casesAPI.unreadCount();
      setUnread(data.unread || 0);
    } catch {
      /* silent — bell is non-critical */
    }
  }, []);

  useEffect(() => {
    refreshCount();
    const t = setInterval(refreshCount, POLL_MS);
    return () => clearInterval(t);
  }, [refreshCount]);

  // Close dropdown on outside click
  useEffect(() => {
    const onClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  const toggle = async () => {
    const next = !open;
    setOpen(next);
    if (next) {
      setLoading(true);
      try {
        const { data } = await casesAPI.listNotifications();
        setItems(data);
      } catch {
        setItems([]);
      } finally {
        setLoading(false);
      }
    }
  };

  const markRead = async (id) => {
    try {
      await casesAPI.markRead(id);
      setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
      setUnread((u) => Math.max(0, u - 1));
    } catch { /* ignore */ }
  };

  const markAllRead = async () => {
    try {
      await casesAPI.markAllRead();
      setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnread(0);
    } catch { /* ignore */ }
  };

  const timeAgo = (ts) => {
    if (!ts) return '';
    const diff = (Date.now() - new Date(ts).getTime()) / 1000;
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button
        className="btn btn-ghost"
        style={{ padding: '8px', position: 'relative' }}
        onClick={toggle}
        aria-label="Notifications"
      >
        <Bell size={18} />
        {unread > 0 && (
          <span style={{
            position: 'absolute', top: 2, right: 2, minWidth: 16, height: 16,
            padding: '0 4px', borderRadius: 8, background: 'var(--accent-red, #ef4444)',
            color: '#fff', fontSize: '0.62rem', fontWeight: 700, lineHeight: '16px',
            textAlign: 'center',
          }}>
            {unread > 9 ? '9+' : unread}
          </span>
        )}
      </button>

      {open && (
        <div style={{
          position: 'absolute', right: 0, top: 'calc(100% + 8px)', width: 340,
          maxHeight: 420, overflowY: 'auto', zIndex: 100,
          background: 'var(--bg-card, #131a2a)', border: '1px solid var(--border, #233)',
          borderRadius: 10, boxShadow: '0 12px 32px rgba(0,0,0,0.4)',
        }}>
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '12px 14px', borderBottom: '1px solid var(--border, #233)',
          }}>
            <strong style={{ fontSize: '0.85rem' }}>Notifications</strong>
            {items.some((n) => !n.is_read) && (
              <button className="btn btn-ghost btn-sm" onClick={markAllRead} title="Mark all read"
                style={{ fontSize: '0.72rem', display: 'flex', gap: 4, alignItems: 'center' }}>
                <CheckCheck size={13} /> Mark all read
              </button>
            )}
          </div>

          {loading ? (
            <div style={{ padding: 24, textAlign: 'center' }}><div className="spinner" style={{ width: 20, height: 20, margin: '0 auto' }} /></div>
          ) : items.length === 0 ? (
            <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
              No notifications yet
            </div>
          ) : (
            items.map((n) => (
              <div key={n.id} style={{
                padding: '10px 14px', borderBottom: '1px solid var(--border, #233)',
                background: n.is_read ? 'transparent' : 'var(--bg-card-hover, rgba(59,130,246,0.06))',
                display: 'flex', gap: 8, alignItems: 'flex-start',
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary, #e6e9ef)' }}>
                    {n.title}
                  </div>
                  {n.message && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary, #aab)', marginTop: 2 }}>
                      {n.message}
                    </div>
                  )}
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    {timeAgo(n.created_at)}
                  </div>
                </div>
                {!n.is_read && (
                  <button className="btn btn-ghost btn-sm" onClick={() => markRead(n.id)}
                    title="Mark read" style={{ padding: 4 }}>
                    <Check size={14} />
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
