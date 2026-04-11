import { Search, Bell } from 'lucide-react';
import { useLocation } from 'react-router-dom';

const pageTitles = {
  '/': 'Dashboard',
  '/fir-analyzer': 'FIR Analyzer',
  '/case-intelligence': 'Case Intelligence',
  '/legal-assistant': 'Legal Assistant',
  '/mo-patterns': 'MO Patterns',
  '/translation': 'Translation',
};

export default function Header() {
  const { pathname } = useLocation();
  const title = pageTitles[pathname] || 'FirAI';

  return (
    <header className="header">
      <h2 className="header-title">{title}</h2>
      <div className="header-actions">
        <div className="header-search">
          <Search size={16} color="var(--text-muted)" />
          <input type="text" placeholder="Search FIRs, cases..." />
        </div>
        <button className="btn btn-ghost" style={{ padding: '8px' }}>
          <Bell size={18} />
        </button>
      </div>
    </header>
  );
}
