import { useState } from 'react';
import { Filter, X, ChevronDown } from 'lucide-react';

/**
 * Advanced Filters Component
 * Provides date range, status, accused name, and crime type filters
 */
export function AdvancedFilters({ onFilterChange, initialFilters = {} }) {
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState({
    crimeType: initialFilters.crimeType || '',
    severity: initialFilters.severity || '',
    policeStation: initialFilters.policeStation || '',
    status: initialFilters.status || '',
    accusedName: initialFilters.accusedName || '',
    dateFrom: initialFilters.dateFrom || '',
    dateTo: initialFilters.dateTo || '',
  });

  const crimeTypes = ['theft', 'assault', 'fraud', 'robbery', 'murder', 'rape', 'burglary'];
  const severities = ['low', 'medium', 'high', 'critical'];
  const statuses = ['new', 'under-investigation', 'closed', 'pending'];
  const policeStations = ['Kalpakancherry', 'Vaikom', 'Ettumanoor', 'Erumeli'];

  const handleFilterChange = (field, value) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
  };

  const handleApply = () => {
    onFilterChange(filters);
    setIsOpen(false);
  };

  const handleReset = () => {
    const emptyFilters = {
      crimeType: '',
      severity: '',
      policeStation: '',
      status: '',
      accusedName: '',
      dateFrom: '',
      dateTo: '',
    };
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
    setIsOpen(false);
  };

  const activeFilterCount = Object.values(filters).filter(v => v).length;

  return (
    <div className="relative">
      {/* Filter button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="btn-secondary flex items-center gap-2"
      >
        <Filter className="w-4 h-4" />
        Filters
        {activeFilterCount > 0 && (
          <span className="ml-1 px-2 py-0.5 bg-status-info text-white text-xs rounded-full">
            {activeFilterCount}
          </span>
        )}
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Filter panel */}
      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-96 bg-primary border border-default rounded-lg shadow-lg z-20 p-4">
          <div className="space-y-4">
            {/* Crime Type */}
            <div>
              <label className="block text-sm font-semibold text-primary mb-2">
                Crime Type
              </label>
              <select
                value={filters.crimeType}
                onChange={(e) => handleFilterChange('crimeType', e.target.value)}
                className="w-full px-3 py-2 border border-default rounded-md bg-secondary text-primary"
              >
                <option value="">All Crime Types</option>
                {crimeTypes.map(type => (
                  <option key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
                ))}
              </select>
            </div>

            {/* Severity */}
            <div>
              <label className="block text-sm font-semibold text-primary mb-2">
                Severity
              </label>
              <select
                value={filters.severity}
                onChange={(e) => handleFilterChange('severity', e.target.value)}
                className="w-full px-3 py-2 border border-default rounded-md bg-secondary text-primary"
              >
                <option value="">All Severities</option>
                {severities.map(sev => (
                  <option key={sev} value={sev}>{sev.charAt(0).toUpperCase() + sev.slice(1)}</option>
                ))}
              </select>
            </div>

            {/* Police Station */}
            <div>
              <label className="block text-sm font-semibold text-primary mb-2">
                Police Station
              </label>
              <select
                value={filters.policeStation}
                onChange={(e) => handleFilterChange('policeStation', e.target.value)}
                className="w-full px-3 py-2 border border-default rounded-md bg-secondary text-primary"
              >
                <option value="">All Stations</option>
                {policeStations.map(station => (
                  <option key={station} value={station}>{station}</option>
                ))}
              </select>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-semibold text-primary mb-2">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-default rounded-md bg-secondary text-primary"
              >
                <option value="">All Status</option>
                {statuses.map(status => (
                  <option key={status} value={status}>{status.replace('-', ' ').toUpperCase()}</option>
                ))}
              </select>
            </div>

            {/* Accused Name */}
            <div>
              <label className="block text-sm font-semibold text-primary mb-2">
                Accused Name
              </label>
              <input
                type="text"
                value={filters.accusedName}
                onChange={(e) => handleFilterChange('accusedName', e.target.value)}
                placeholder="Search accused..."
                className="w-full px-3 py-2 border border-default rounded-md bg-secondary text-primary"
              />
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-semibold text-primary mb-2">
                  From Date
                </label>
                <input
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                  className="w-full px-3 py-2 border border-default rounded-md bg-secondary text-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-primary mb-2">
                  To Date
                </label>
                <input
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                  className="w-full px-3 py-2 border border-default rounded-md bg-secondary text-primary"
                />
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex gap-2 pt-4 border-t border-default">
              <button
                onClick={handleApply}
                className="flex-1 btn-primary"
              >
                Apply Filters
              </button>
              <button
                onClick={handleReset}
                className="flex-1 btn-secondary"
              >
                Reset
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="btn-secondary p-2"
                title="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Active Filters Display
 * Shows applied filters as removable chips
 */
export function ActiveFilters({ filters, onRemoveFilter, onClearAll }) {
  const displayNames = {
    crimeType: 'Crime Type',
    severity: 'Severity',
    policeStation: 'Station',
    status: 'Status',
    accusedName: 'Accused',
    dateFrom: 'From',
    dateTo: 'To',
  };

  const activeFilters = Object.entries(filters).filter(([_, value]) => value);

  if (activeFilters.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 p-3 bg-tertiary rounded-lg">
      {activeFilters.map(([key, value]) => (
        <div
          key={key}
          className="flex items-center gap-2 bg-primary px-3 py-1 rounded-full border border-default"
        >
          <span className="text-sm font-medium">
            {displayNames[key]}: <strong>{value}</strong>
          </span>
          <button
            onClick={() => onRemoveFilter(key)}
            className="hover:text-error transition-colors"
            title={`Remove ${displayNames[key]} filter`}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}

      <button
        onClick={onClearAll}
        className="ml-auto text-sm text-secondary hover:text-primary underline"
      >
        Clear all
      </button>
    </div>
  );
}
