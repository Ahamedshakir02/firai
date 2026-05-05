import { useState, useEffect } from 'react';
import { firAPI } from '../api/client';
import { Search, Filter, Eye, Calendar, MapPin, ChevronRight, X, Download } from 'lucide-react';

export default function CaseIntelligence() {
  const [firs, setFirs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFIR, setSelectedFIR] = useState(null);
  const [similarFIRs, setSimilarFIRs] = useState([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('');
  const [policeStation, setPoliceStation] = useState('');

  useEffect(() => { loadFIRs(); }, []);

  const loadFIRs = async () => {
    try {
      const params = {};
      if (searchQuery) params.search = searchQuery;
      if (filterType) params.crime_type = filterType;
      if (policeStation) params.police_station = policeStation;
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

  const downloadFIR = async (fir) => {
    try {
      const response = await firAPI.downloadFIR(fir.id);
      const isPDF = response.headers['content-type']?.includes('pdf') || response.headers['content-type'] === 'application/pdf';
      const filename = isPDF ? `FIR-${fir.fir_number || fir.id}.pdf` : `FIR-${fir.fir_number || fir.id}.json`;
      
      const blob = new Blob([response.data], { type: isPDF ? 'application/pdf' : 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const exportAllFIRs = async () => {
    try {
      const { data } = await firAPI.exportAll();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'all_firs_export.json';
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  // Crime types from actual classifier output
  const CRIME_TYPES = [
    { value: 'abetment_of_suicide', label: 'Abetment of Suicide' },
    { value: 'assault', label: 'Assault' },
    { value: 'cheating', label: 'Cheating' },
    { value: 'criminal_intimidation', label: 'Criminal Intimidation' },
    { value: 'cyber_crime', label: 'Cyber Crime' },
    { value: 'dacoity', label: 'Dacoity' },
    { value: 'domestic_violence', label: 'Domestic Violence' },
    { value: 'drug_offense', label: 'Drug Offense' },
    { value: 'drunk_driving', label: 'Drunk Driving' },
    { value: 'forgery', label: 'Forgery' },
    { value: 'kidnapping', label: 'Kidnapping' },
    { value: 'murder', label: 'Murder' },
    { value: 'property_damage', label: 'Property Damage' },
    { value: 'rash_driving', label: 'Rash Driving' },
    { value: 'robbery', label: 'Robbery' },
    { value: 'sexual_offense', label: 'Sexual Offense' },
    { value: 'theft', label: 'Theft' },
    { value: 'trespass', label: 'Trespass' },
    { value: 'unnatural_death', label: 'Unnatural Death' },
    { value: 'other', label: 'Other' },
  ];

  // Police stations extracted from actual FIR PDFs
  const POLICE_STATIONS = [
    'AMBALAPUZHA', 'CHALISSERRY', 'CHERPULASSERRY', 'CHITTOOR', 'CYBER',
    'EDAKKARA', 'ELOOR', 'ERAVIPURAM', 'ERNAKULAM', 'FEROKE', 'FORT',
    'KALAMASSERRY', 'KALIYAR', 'KALPAKANCHERRY', 'KANNUR', 'KASARGODE',
    'KATTAPPANA', 'KAZHAKUTTAM', 'KENICHIRA', 'KOTTAKKAL', 'MALAPPURAM',
    'MAVOOR', 'MEDICAL', 'NILAMBUR', 'PINARAYI', 'POOJAPPURA',
    'PULIKEEZHU', 'THRITHALA', 'TIRUR', 'WADAKKANCHERRY',
  ];

  return (
    <>
      <h1 className="page-title">Case Intelligence</h1>
      <p className="page-description">Browse FIRs, find similar cases based on narrative patterns</p>

      {/* Search & Filter */}
      <div className="card" style={{ marginBottom: 24, padding: 16 }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <div className="header-search" style={{ flex: 1, minWidth: 200 }}>
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
            {CRIME_TYPES.map((ct) => (
              <option key={ct.value} value={ct.value}>{ct.label}</option>
            ))}
          </select>
          <select
            className="form-select"
            style={{ width: 180 }}
            value={policeStation}
            onChange={(e) => { setPoliceStation(e.target.value); setLoading(true); setTimeout(loadFIRs, 100); }}
          >
            <option value="">All Stations</option>
            {POLICE_STATIONS.map((ps) => (
              <option key={ps} value={ps}>
                {ps.charAt(0) + ps.slice(1).toLowerCase().replace(/(^|\s)\w/g, (c) => c.toUpperCase())}
              </option>
            ))}
          </select>
          <button type="submit" className="btn btn-primary">
            <Filter size={16} /> Filter
          </button>
          <button type="button" className="btn btn-ghost" onClick={exportAllFIRs} title="Export all FIRs as JSON">
            <Download size={16} /> Export All
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
                      {fir.file_name ? fir.file_name.replace(/\.(json|pdf|txt)$/i, '') : (fir.fir_number ? `Case ${fir.fir_number} — ${fir.police_station || ''}` : `FIR #${fir.id}`)}
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
                    {fir.police_station && (
                      <span><MapPin size={12} /> {fir.police_station}</span>
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
                {selectedFIR.file_name ? selectedFIR.file_name.replace(/\.(json|pdf|txt)$/i, '') : (selectedFIR.fir_number ? `Case ${selectedFIR.fir_number}` : `FIR #${selectedFIR.id}`)}
                {!selectedFIR.file_name && selectedFIR.police_station && (
                  <span style={{ fontSize: '0.8rem', fontWeight: 400, color: 'var(--text-muted)', marginLeft: 8 }}>
                    {selectedFIR.police_station} PS
                  </span>
                )}
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => downloadFIR(selectedFIR)} title="Download FIR Document">
                <Download size={14} />
              </button>
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

            {/* Place & Station */}
            {(selectedFIR.place || selectedFIR.police_station) && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 18 }}>
                {selectedFIR.police_station && (
                  <div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Police Station</div>
                    <span style={{ fontSize: '0.83rem', color: 'var(--text-secondary)' }}>{selectedFIR.police_station}</span>
                  </div>
                )}
                {selectedFIR.place && (
                  <div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Place</div>
                    <span style={{ fontSize: '0.83rem', color: 'var(--text-secondary)' }}>{selectedFIR.place}</span>
                  </div>
                )}
              </div>
            )}

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
