import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, User, Lock, Loader, AlertCircle, UserPlus } from 'lucide-react';

export default function Login() {
  const { login } = useAuth();
  const [mode, setMode] = useState('login'); // login | register
  const [badge, setBadge] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Registration fields
  const [regData, setRegData] = useState({
    name: '', badge_number: '', rank: '', police_station: '',
    district: '', phone: '', email: '', password: '',
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!badge.trim() || !password.trim()) return;
    setLoading(true);
    setError('');
    try {
      await login(badge, password);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!regData.name || !regData.badge_number || !regData.password) return;
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const API_BASE = import.meta.env.VITE_API_URL || '/api';
      await fetch(`${API_BASE}/auth/register-request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(regData),
      }).then(async (res) => {
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || 'Registration failed');
        }
        return res.json();
      });
      setSuccess('Registration request submitted! Please wait for admin approval.');
      setRegData({ name: '', badge_number: '', rank: '', police_station: '', district: '', phone: '', email: '', password: '' });
    } catch (err) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0f172a 100%)',
      padding: 20,
    }}>
      <div style={{
        width: '100%', maxWidth: mode === 'register' ? 520 : 420,
        background: 'rgba(17, 24, 39, 0.85)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(99, 102, 241, 0.15)',
        borderRadius: 16, padding: 40,
        boxShadow: '0 25px 50px rgba(0, 0, 0, 0.5)',
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{
            width: 60, height: 60, borderRadius: '50%',
            background: 'linear-gradient(135deg, #6366f1, #3b82f6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px',
          }}>
            <Shield size={28} color="white" />
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f1f5f9', margin: 0 }}>FirAI</h1>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: 4 }}>
            Kerala Police AI Investigation Assistant
          </p>
        </div>

        {/* Mode Tabs */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
          <button
            onClick={() => { setMode('login'); setError(''); setSuccess(''); }}
            style={{
              flex: 1, padding: '10px 0', border: 'none', borderRadius: 8, cursor: 'pointer',
              fontWeight: 600, fontSize: '0.85rem', transition: 'all 0.2s',
              background: mode === 'login' ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
              color: mode === 'login' ? '#818cf8' : '#64748b',
              border: mode === 'login' ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid transparent',
            }}
          >
            <User size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} /> Sign In
          </button>
          <button
            onClick={() => { setMode('register'); setError(''); setSuccess(''); }}
            style={{
              flex: 1, padding: '10px 0', border: 'none', borderRadius: 8, cursor: 'pointer',
              fontWeight: 600, fontSize: '0.85rem', transition: 'all 0.2s',
              background: mode === 'register' ? 'rgba(16, 185, 129, 0.2)' : 'transparent',
              color: mode === 'register' ? '#34d399' : '#64748b',
              border: mode === 'register' ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid transparent',
            }}
          >
            <UserPlus size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} /> Request Access
          </button>
        </div>

        {/* Login Form */}
        {mode === 'login' && (
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: 6, fontWeight: 500 }}>
                Badge Number
              </label>
              <div style={{ position: 'relative' }}>
                <User size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                <input
                  type="text" value={badge} onChange={(e) => setBadge(e.target.value)}
                  placeholder="e.g. KP-1001"
                  style={{
                    width: '100%', padding: '12px 12px 12px 38px', border: '1px solid rgba(99, 102, 241, 0.2)',
                    borderRadius: 8, background: 'rgba(15, 23, 42, 0.6)', color: '#f1f5f9',
                    fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box',
                  }}
                />
              </div>
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: 6, fontWeight: 500 }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                <input
                  type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  style={{
                    width: '100%', padding: '12px 12px 12px 38px', border: '1px solid rgba(99, 102, 241, 0.2)',
                    borderRadius: 8, background: 'rgba(15, 23, 42, 0.6)', color: '#f1f5f9',
                    fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box',
                  }}
                />
              </div>
            </div>

            <button
              type="submit" disabled={loading || !badge.trim() || !password.trim()}
              style={{
                width: '100%', padding: '13px 0', border: 'none', borderRadius: 8, cursor: 'pointer',
                fontWeight: 600, fontSize: '0.9rem',
                background: 'linear-gradient(135deg, #6366f1, #3b82f6)',
                color: 'white', opacity: loading ? 0.7 : 1, transition: 'opacity 0.2s',
              }}
            >
              {loading ? <><Loader size={16} style={{ animation: 'spin 1s linear infinite', verticalAlign: 'middle' }} /> Signing in...</> : 'Sign In'}
            </button>
          </form>
        )}

        {/* Registration Form */}
        {mode === 'register' && (
          <form onSubmit={handleRegister}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
              {[
                { key: 'name', label: 'Full Name *', placeholder: 'Officer Name', span: 2 },
                { key: 'badge_number', label: 'Badge Number *', placeholder: 'KP-XXXX' },
                { key: 'rank', label: 'Rank', placeholder: 'SI / ASI / CI' },
                { key: 'police_station', label: 'Police Station', placeholder: 'Station name' },
                { key: 'district', label: 'District', placeholder: 'District' },
                { key: 'phone', label: 'Phone', placeholder: '+91 ...' },
                { key: 'email', label: 'Email', placeholder: 'email@keralapolice.gov.in' },
                { key: 'password', label: 'Password *', placeholder: 'Min 6 characters', type: 'password', span: 2 },
              ].map((field) => (
                <div key={field.key} style={{ gridColumn: field.span === 2 ? '1 / -1' : undefined }}>
                  <label style={{ fontSize: '0.72rem', color: '#94a3b8', display: 'block', marginBottom: 4, fontWeight: 500 }}>
                    {field.label}
                  </label>
                  <input
                    type={field.type || 'text'}
                    value={regData[field.key]}
                    onChange={(e) => setRegData({ ...regData, [field.key]: e.target.value })}
                    placeholder={field.placeholder}
                    style={{
                      width: '100%', padding: '10px 12px', border: '1px solid rgba(16, 185, 129, 0.2)',
                      borderRadius: 8, background: 'rgba(15, 23, 42, 0.6)', color: '#f1f5f9',
                      fontSize: '0.82rem', outline: 'none', boxSizing: 'border-box',
                    }}
                  />
                </div>
              ))}
            </div>

            <button
              type="submit" disabled={loading || !regData.name || !regData.badge_number || !regData.password}
              style={{
                width: '100%', padding: '13px 0', border: 'none', borderRadius: 8, cursor: 'pointer',
                fontWeight: 600, fontSize: '0.9rem', marginTop: 8,
                background: 'linear-gradient(135deg, #10b981, #059669)',
                color: 'white', opacity: loading ? 0.7 : 1, transition: 'opacity 0.2s',
              }}
            >
              {loading ? <><Loader size={16} style={{ animation: 'spin 1s linear infinite', verticalAlign: 'middle' }} /> Submitting...</> : 'Submit Registration Request'}
            </button>
          </form>
        )}

        {/* Error/Success Messages */}
        {error && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 16, padding: 12, borderRadius: 8, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#f87171', fontSize: '0.82rem' }}>
            <AlertCircle size={16} /> {error}
          </div>
        )}
        {success && (
          <div style={{ marginTop: 16, padding: 12, borderRadius: 8, background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.2)', color: '#34d399', fontSize: '0.82rem' }}>
            ✓ {success}
          </div>
        )}

        {/* Demo Credentials */}
        {mode === 'login' && (
          <div style={{ marginTop: 20, padding: 12, borderRadius: 8, background: 'rgba(99, 102, 241, 0.06)', border: '1px solid rgba(99, 102, 241, 0.1)', fontSize: '0.75rem', color: '#64748b' }}>
            <div style={{ fontWeight: 600, marginBottom: 6, color: '#94a3b8' }}>Demo Credentials</div>
            <div>Badge: <strong style={{ color: '#818cf8' }}>KP-1001</strong> | Password: <strong style={{ color: '#818cf8' }}>firai123</strong></div>
          </div>
        )}
      </div>
    </div>
  );
}
