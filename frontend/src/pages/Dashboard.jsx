import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../../api/client';
import {
  FileText, AlertTriangle, Shield, TrendingUp,
  Clock, ChevronRight
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';

const COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#ec4899'];

const severityColor = {
  low: 'var(--severity-low)',
  medium: 'var(--severity-medium)',
  high: 'var(--severity-high)',
  critical: 'var(--severity-critical)',
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const { data } = await dashboardAPI.getStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-overlay">
        <div className="spinner" />
        <span>Loading dashboard...</span>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="empty-state">
        <Shield className="empty-icon" size={64} />
        <div className="empty-title">No Data Available</div>
        <div className="empty-text">Upload FIRs to see dashboard statistics</div>
      </div>
    );
  }

  const crimeData = Object.entries(stats.crime_type_breakdown || {}).map(([name, value]) => ({
    name: name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value,
  }));

  const severityData = Object.entries(stats.severity_breakdown || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
    color: severityColor[name] || 'var(--accent-blue)',
  }));

  return (
    <>
      <h1 className="page-title">Investigation Dashboard</h1>
      <p className="page-description">Real-time overview of FIR analysis and crime intelligence</p>

      {/* Stat Cards */}
      <div className="stat-grid">
        <div className="stat-card" style={{ '--stat-color': 'var(--accent-blue)' }}>
          <div className="stat-icon"><FileText size={22} /></div>
          <div className="stat-value">{stats.total_firs}</div>
          <div className="stat-label">Total FIRs</div>
        </div>

        <div className="stat-card" style={{ '--stat-color': 'var(--accent-gold)' }}>
          <div className="stat-icon"><AlertTriangle size={22} /></div>
          <div className="stat-value">{stats.severity_breakdown?.high || 0}</div>
          <div className="stat-label">High Severity</div>
        </div>

        <div className="stat-card" style={{ '--stat-color': 'var(--accent-red)' }}>
          <div className="stat-icon"><Shield size={22} /></div>
          <div className="stat-value">{stats.severity_breakdown?.critical || 0}</div>
          <div className="stat-label">Critical Cases</div>
        </div>

        <div className="stat-card" style={{ '--stat-color': 'var(--accent-emerald)' }}>
          <div className="stat-icon"><TrendingUp size={22} /></div>
          <div className="stat-value">{Object.keys(stats.crime_type_breakdown || {}).length}</div>
          <div className="stat-label">Crime Types</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid-2" style={{ marginBottom: 28 }}>
        {/* Crime Type Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Crime Type Distribution</div>
              <div className="card-subtitle">Based on narrative analysis</div>
            </div>
          </div>
          {crimeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={crimeData}>
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: '#1a2942', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, color: '#f1f5f9' }}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {crimeData.map((_, idx) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state" style={{ padding: 32 }}>
              <div className="empty-text">No crime data yet</div>
            </div>
          )}
        </div>

        {/* Severity Chart */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Severity Distribution</div>
              <div className="card-subtitle">Risk assessment from narratives</div>
            </div>
          </div>
          {severityData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={severityData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} innerRadius={55} paddingAngle={3}>
                  {severityData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1a2942', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, color: '#f1f5f9' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state" style={{ padding: 32 }}>
              <div className="empty-text">No severity data yet</div>
            </div>
          )}
          <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 8 }}>
            {severityData.map((item) => (
              <div key={item.name} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem' }}>
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: item.color }} />
                <span style={{ color: 'var(--text-muted)' }}>{item.name}: {item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent FIRs Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Recent FIRs</div>
            <div className="card-subtitle">Latest processed FIR narratives</div>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/case-intelligence')}>
            View All <ChevronRight size={14} />
          </button>
        </div>

        {stats.recent_firs?.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>File</th>
                <th>Crime Type</th>
                <th>Severity</th>
                <th>Narrative Preview</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_firs.map((fir) => (
                <tr key={fir.id} onClick={() => navigate(`/case-intelligence?fir=${fir.id}`)}>
                  <td style={{ fontWeight: 600, color: 'var(--accent-blue-light)' }}>#{fir.id}</td>
                  <td>{fir.file_name || '—'}</td>
                  <td>
                    <span className="badge badge-blue">
                      {(fir.crime_type || 'unknown').replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-${fir.severity || 'medium'}`}>
                      {fir.severity || 'N/A'}
                    </span>
                  </td>
                  <td style={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {fir.narrative?.slice(0, 80) || '—'}...
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>
                    <Clock size={12} style={{ marginRight: 4 }} />
                    {fir.fir_date || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state" style={{ padding: 32 }}>
            <div className="empty-text">No FIRs processed yet. Upload FIRs to get started.</div>
          </div>
        )}
      </div>
    </>
  );
}
