import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard, FileSearch, Brain, Scale,
  Fingerprint, Languages, Shield, User, LogOut, Badge
} from 'lucide-react';

const navItems = [
  { label: 'OVERVIEW', items: [
    { to: '/', icon: LayoutDashboard, text: 'Dashboard' },
  ]},
  { label: 'INVESTIGATION', items: [
    { to: '/fir-analyzer', icon: FileSearch, text: 'FIR Analyzer' },
    { to: '/case-intelligence', icon: Brain, text: 'Case Intelligence' },
    { to: '/mo-patterns', icon: Fingerprint, text: 'MO Patterns' },
  ]},
  { label: 'SUPPORT', items: [
    { to: '/legal-assistant', icon: Scale, text: 'Legal Assistant' },
    { to: '/translation', icon: Languages, text: 'Translation' },
  ]},
];

export default function Sidebar() {
  const { officer, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">
          <Shield size={22} />
        </div>
        <div className="logo-text">
          <h1>FirAI</h1>
          <span>Kerala Police Investigation</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((section) => (
          <div key={section.label}>
            <div className="sidebar-section-label">{section.label}</div>
            {section.items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? 'active' : ''}`
                }
                end={item.to === '/'}
              >
                <item.icon className="link-icon" size={20} />
                {item.text}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* Officer Info & Actions */}
      {officer && (
        <div style={{
          marginTop: 'auto', padding: '12px 16px',
          borderTop: '1px solid var(--border-color)',
        }}>
          {/* Profile Link */}
          <NavLink
            to="/profile"
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            style={{ marginBottom: 8 }}
          >
            <User className="link-icon" size={20} />
            Profile
          </NavLink>

          {/* Officer Card */}
          <div style={{
            padding: '10px 12px', borderRadius: 8,
            background: 'rgba(99, 102, 241, 0.06)',
            border: '1px solid rgba(99, 102, 241, 0.1)',
            marginBottom: 8,
          }}>
            <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>
              {officer.name}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              <Badge size={10} /> {officer.badge_number}
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 2 }}>
              {officer.police_station || officer.rank || ''}
            </div>
          </div>

          {/* Logout */}
          <button
            onClick={handleLogout}
            style={{
              width: '100%', padding: '8px 12px', border: 'none', borderRadius: 8,
              background: 'rgba(239, 68, 68, 0.08)', color: '#f87171',
              fontSize: '0.8rem', fontWeight: 500, cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 8,
              transition: 'background 0.2s',
            }}
            onMouseEnter={(e) => e.target.style.background = 'rgba(239, 68, 68, 0.15)'}
            onMouseLeave={(e) => e.target.style.background = 'rgba(239, 68, 68, 0.08)'}
          >
            <LogOut size={14} /> Sign Out
          </button>
        </div>
      )}
    </aside>
  );
}
