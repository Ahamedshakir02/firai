import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, FileSearch, Brain, Scale,
  Fingerprint, Languages, Shield
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
    </aside>
  );
}
