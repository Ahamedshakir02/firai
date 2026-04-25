import { useAuth } from '../context/AuthContext';
import { Shield, MapPin, Phone, Mail, Badge, Building2, Star } from 'lucide-react';

export default function Profile() {
  const { officer } = useAuth();

  if (!officer) return null;

  const fields = [
    { icon: Badge, label: 'Badge Number', value: officer.badge_number, color: '#6366f1' },
    { icon: Star, label: 'Rank', value: officer.rank, color: '#f59e0b' },
    { icon: Building2, label: 'Police Station', value: officer.police_station, color: '#3b82f6' },
    { icon: MapPin, label: 'District', value: officer.district, color: '#10b981' },
    { icon: Phone, label: 'Phone', value: officer.phone, color: '#8b5cf6' },
    { icon: Mail, label: 'Email', value: officer.email, color: '#ec4899' },
  ];

  return (
    <>
      <h1 className="page-title">Officer Profile</h1>
      <p className="page-description">Your identity and station details</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, maxWidth: 800 }}>
        {/* Profile Card */}
        <div className="card" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: 32 }}>
          <div style={{
            width: 80, height: 80, borderRadius: '50%',
            background: 'linear-gradient(135deg, #6366f1, #3b82f6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px',
            boxShadow: '0 8px 24px rgba(99, 102, 241, 0.3)',
          }}>
            <Shield size={36} color="white" />
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 4px' }}>
            {officer.name}
          </h2>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginTop: 8 }}>
            <span className="badge badge-blue" style={{ fontSize: '0.82rem' }}>{officer.rank || 'Officer'}</span>
            {officer.is_admin && (
              <span className="badge badge-critical" style={{ fontSize: '0.72rem' }}>Admin</span>
            )}
          </div>
        </div>

        {/* Detail Cards */}
        {fields.map((f, i) => (
          <div key={i} className="card" style={{ padding: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: `${f.color}15`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <f.icon size={18} color={f.color} />
              </div>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 2 }}>
                  {f.label}
                </div>
                <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {f.value || '—'}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
