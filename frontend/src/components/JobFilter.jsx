import React from 'react';
import { Search, Filter, RotateCcw } from 'lucide-react';

export const JobFilter = ({ filters, onFilterChange, onReset }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    onFilterChange(name, value);
  };

  return (
    <div className="filter-panel">
      <div className="form-group" style={{ flex: '2', minWidth: '220px' }}>
        <label className="form-label">Job Role / Title</label>
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            name="role"
            value={filters.role || ''}
            onChange={handleChange}
            placeholder="Search role e.g. Frontend Developer"
            className="input-control"
            style={{ paddingLeft: '2.2rem' }}
          />
          <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Tech Skill</label>
        <input
          type="text"
          name="skill"
          value={filters.skill || ''}
          onChange={handleChange}
          placeholder="e.g. Python, React"
          className="input-control"
        />
      </div>

      <div className="form-group">
        <label className="form-label">Location / City</label>
        <input
          type="text"
          name="location"
          value={filters.location || ''}
          onChange={handleChange}
          placeholder="e.g. New York, London"
          className="input-control"
        />
      </div>

      <div className="form-group">
        <label className="form-label">Experience Tier</label>
        <select
          name="experience_level"
          value={filters.experience_level || ''}
          onChange={handleChange}
          className="select-control"
        >
          <option value="">All Levels</option>
          <option value="Entry-level">Entry-level</option>
          <option value="Junior">Junior</option>
          <option value="Mid-level">Mid-level</option>
          <option value="Senior">Senior</option>
          <option value="Lead">Lead</option>
        </select>
      </div>

      <div className="form-group">
        <label className="form-label">Remote Work</label>
        <select
          name="remote_type"
          value={filters.remote_type || ''}
          onChange={handleChange}
          className="select-control"
        >
          <option value="">All Types</option>
          <option value="Remote">Remote</option>
          <option value="Hybrid">Hybrid</option>
          <option value="On-site">On-site</option>
        </select>
      </div>

      <div style={{ display: 'flex', alignItems: 'flex-end', height: '100%', paddingTop: '1.25rem' }}>
        <button className="btn btn-secondary" onClick={onReset} title="Reset all filters">
          <RotateCcw size={16} />
          <span>Reset</span>
        </button>
      </div>
    </div>
  );
};
