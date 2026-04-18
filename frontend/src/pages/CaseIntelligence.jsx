import { useState, useEffect } from 'react';
import { firAPI } from '../api/client';
import { Search, Filter, Eye, Calendar, MapPin, ChevronRight, X } from 'lucide-react';

export default function CaseIntelligence() {
  const [firs, setFirs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFIR, setSelectedFIR] = useState(null);
  const [similarFIRs, setSimilarFIRs] = useState([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('');

  useEffect(() => { loadFIRs(); }, []);

  const loadFIRs = async () => {
    try {
      const params = {};
      if (searchQuery) params.search = searchQuery;
      if (filterType) params.crime_type = filterType;
      const { data } = await firAPI.list(params);
      setFirs(data);
    } catch (err) {
      console.error('Failed to load FIRs:', err);
    } finally {
      setLoading(false);
    }
  };

  const viewFIR = async (fir) => {
    try {
      const { data } = await firAPI.get(fir.id);
      setSelectedFIR(data);
      setLoadingSimilar(true);
      const { data: similar } = await firAPI.getSimilar(fir.id);
      setSimilarFIRs(similar);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingSimilar(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setLoading(true);
    loadFIRs();
  };

  return (
    <>
      <h1 className="page-title">Case Intelligence</h1>
      <p className="page-description">Browse FIRs, find similar cases based on narrative patterns</p>

      {/* Search & Filter */}
      <div className="card" style={{ marginBottom: 24, padding: 16 }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <div className="header-search" style={{ flex: 1 }}>
            <Search size={16} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Search narratives..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <select
            className="form-select"
            style={{ width: 180 }}
            value={filterType}
            onChange={(e) => { setFilterType(e.target.value); setLoading(true); setTimeout(loadFIRs, 100); }}
          >
            <option value="">All Crime Types</option>
            <option value="assault">Assault</option>
            <option value="theft">Theft</option>
            <option value="cheating">Cheating</option>
            <option value="trespass">Trespass</option>
            <option value="murder">Murder</option>
            <option value="other">Other</option>
          </select>
          <button type="submit" className="btn btn-primary">
            <Filter size={16} /> Filter
          </button>
        </form>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selectedFIR ? '1fr 1fr' : '1fr', gap: 24 }}>
        {/* FIR List */}
        <div>
          {loading ? (
            <div className="loading-overlay"><div className="spinner" /><span>Loading FIRs...</span></div>
          ) : firs.length === 0 ? (
            <div className="empty-state">
              <div className="empty-title">No FIRs Found</div>
              <div className="empty-text">Upload FIRs using the FIR Analyzer to populate the database</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {firs.map((fir) => (
                <div
                  key={fir.id}
                  className="fir-card"
                  onClick={() => viewFIR(fir)}
                  style={selectedFIR?.id === fir.id ? { borderColor: 'var(--accent-blue)', background: 'var(--bg-card-hover)' } : {}}
                >
                  <div className="fir-header">
                    <span className="fir-id">
                      {fir.fir_number ? `Case ${fir.fir_number}` : `#${fir.id}`}
                      {fir.police_station ? ` — ${fir.police_station}` : (fir.file_name ? ` — ${fir.file_name}` : '')}
                    </span>
                    <span className={`badge badge-${fir.severity || 'medium'}`}>
                      {fir.severity || 'N/A'}
                    </span>
                  </div>
                  <div className="fir-narrative">
                    {fir.narrative?.slice(0, 150) || 'No narrative available'}
                  </div>
                  <div className="fir-meta">
                    {fir.crime_type && (
                      <span className="badge badge-blue" style={{ fontSize: '0.68rem' }}>
                        {fir.crime_type.replace(/_/g, ' ')}
                      </span>
                    )}
                    {fir.fir_date && (
                      <span><Calendar size={12} /> {fir.fir_date}</span>
                    )}
                    {fir.place && (
                      <span><MapPin size={12} /> {fir.place}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* FIR Detail Panel */}
        {selectedFIR && (
          <div className="card" style={{ position: 'sticky', top: 90, alignSelf: 'start', maxHeight: 'calc(100vh - 120px)', overflowY: 'auto' }}>
            <div className="card-header">
              <div className="card-title">
                {selectedFIR.fir_number ? `Case ${selectedFIR.fir_number}` : `FIR #${selectedFIR.id}`}
                {selectedFIR.police_station && (
                  <span style={{ fontSize: '0.8rem', fontWeight: 400, color: 'var(--text-muted)', marginLeft: 8 }}>
                    {selectedFIR.police_station} PS
                  </span>
                )}
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => { setSelectedFIR(null); setSimilarFIRs([]); }}>
                <X size={16} />
              </button>
            </div>

            {/* Summary Info */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 18 }}>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Crime Type</div>
                <span className="badge badge-blue">{(selectedFIR.crime_type || 'Unknown').replace(/_/g, ' ')}</span>
              </div>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Severity</div>
                <span className={`badge badge-${selectedFIR.severity || 'medium'}`}>{selectedFIR.severity || 'N/A'}</span>
              </div>
            </div>

            {/* Narrative */}
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Narrative
              </div>
              <div className="narrative-box">{selectedFIR.narrative}</div>
            </div>

            {/* English Summary */}
            {selectedFIR.summary_en && (
              <div style={{ marginBottom: 18 }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  English Summary
                </div>
                <div className="narrative-box" style={{ background: 'var(--bg-input)' }}>{selectedFIR.summary_en}</div>
              </div>
            )}

            {/* Acts */}
            {selectedFIR.acts?.length > 0 && (
              <div style={{ marginBottom: 18 }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>Acts & Sections</div>
                {selectedFIR.acts.map((a, i) => (
                  <div key={i} style={{ fontSize: '0.83rem', color: 'var(--text-secondary)', marginBottom: 4 }}>
                    <strong>{a.act || a.section}</strong>: {a.sections?.join(', ') || a.description || ''}
                  </div>
                ))}
              </div>
            )}

            {/* Accused */}
            {selectedFIR.accused?.length > 0 && (
              <div style={{ marginBottom: 18 }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>Accused</div>
                {selectedFIR.accused.map((a, i) => (
                  <div key={i} style={{ fontSize: '0.83rem', color: 'var(--text-secondary)', marginBottom: 4 }}>
                    {a.name}{a.father_name ? ` (S/O ${a.father_name})` : ''}
                  </div>
                ))}
              </div>
            )}

            {/* Similar Cases */}
            <div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Similar Cases by Narrative
              </div>
              {loadingSimilar ? (
                <div className="loading-overlay" style={{ padding: 16 }}>
                  <div className="spinner" style={{ width: 20, height: 20 }} />
                </div>
              ) : similarFIRs.length > 0 ? (
                similarFIRs.map((sim) => (
                  <div key={sim.id} className="fir-card" style={{ marginBottom: 8, padding: 14 }} onClick={() => viewFIR(sim)}>
                    <div className="fir-header">
                      <span className="fir-id">#{sim.id}</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div className="similarity-bar">
                          <div className="fill" style={{ width: `${sim.similarity_score * 100}%` }} />
                        </div>
                        <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                          {(sim.similarity_score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="fir-narrative" style={{ WebkitLineClamp: 2 }}>
                      {sim.narrative || sim.summary_en || 'No preview'}
                    </div>
                  </div>
                ))
              ) : (
                <div style={{ fontSize: '0.83rem', color: 'var(--text-muted)' }}>No similar cases found</div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
