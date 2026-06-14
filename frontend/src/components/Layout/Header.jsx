import { Search, Menu } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import NotificationBell from '../NotificationBell';

const pageTitles = {
  '/': 'Dashboard',
  '/fir-analyzer': 'FIR Analyzer',
  '/case-intelligence': 'Case Intelligence',
  '/legal-assistant': 'Legal Assistant',
  '/mo-patterns': 'MO Patterns',
  '/translation': 'Translation',
};

export default function Header({ onMenuToggle }) {
  const { pathname } = useLocation();
  const title = pageTitles[pathname] || 'FirAI';

  return (
    <header className="header">
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <button
          className="btn btn-ghost mobile-menu-btn"
          onClick={onMenuToggle}
          style={{ padding: '8px' }}
          aria-label="Toggle navigation"
        >
          <Menu size={20} />
        </button>
        <h2 className="header-title">{title}</h2>
      </div>
      <div className="header-actions">
        <div className="header-search">
          <Search size={16} color="var(--text-muted)" />
          <input type="text" placeholder="Search FIRs, cases..." />
        </div>
        <NotificationBell />
      </div>
    </header>
  );
}
