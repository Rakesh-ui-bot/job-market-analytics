import React from 'react';
import { Search, RotateCcw, Filter } from 'lucide-react';
import { useFilters } from '../context/FilterContext';

export const GlobalFilterBar = () => {
  const { filters, setFilter, resetFilters, activeFilterCount } = useFilters();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilter(name, value);
  };

  return (
    <div className="filter-panel" style={{ marginBottom: '1.5rem' }}>
      <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, fontSize: '0.9rem' }}>
          <Filter size={16} color="var(--accent-primary)" />
          <span>Interactive Global Market Filters</span>
          {activeFilterCount > 0 && (
            <span className="badge badge-blue">
              {activeFilterCount} Active {activeFilterCount === 1 ? 'Filter' : 'Filters'}
            </span>
          )}
        </div>

        {activeFilterCount > 0 && (
          <button
            className="btn btn-secondary"
            onClick={resetFilters}
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
          >
            <RotateCcw size={14} />
            <span>Reset All</span>
          </button>
        )}
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', width: '100%' }}>
        {/* Role */}
        <div className="form-group" style={{ flex: '1', minWidth: '160px' }}>
          <label className="form-label">Role Category</label>
          <select
            name="role"
            value={filters.role || ''}
            onChange={handleChange}
            className="select-control"
          >
            <option value="">All Roles</option>
            <option value="Frontend Developer">Frontend Developer</option>
            <option value="Backend Developer">Backend Developer</option>
            <option value="Full Stack Developer">Full Stack Developer</option>
            <option value="Data Scientist">Data Scientist</option>
            <option value="Data Analyst">Data Analyst</option>
            <option value="DevOps Engineer">DevOps Engineer</option>
            <option value="Android Developer">Android Developer</option>
            <option value="QA Engineer">QA Engineer</option>
          </select>
        </div>

        {/* Skill */}
        <div className="form-group" style={{ flex: '1', minWidth: '140px' }}>
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

        {/* Location */}
        <div className="form-group" style={{ flex: '1', minWidth: '140px' }}>
          <label className="form-label">Location</label>
          <input
            type="text"
            name="location"
            value={filters.location || ''}
            onChange={handleChange}
            placeholder="e.g. New York, London"
            className="input-control"
          />
        </div>

        {/* Experience Level */}
        <div className="form-group" style={{ flex: '1', minWidth: '140px' }}>
          <label className="form-label">Experience Tier</label>
          <select
            name="experience_level"
            value={filters.experience_level || ''}
            onChange={handleChange}
            className="select-control"
          >
            <option value="">All Tiers</option>
            <option value="Entry-level">Entry-level</option>
            <option value="Junior">Junior</option>
            <option value="Mid-level">Mid-level</option>
            <option value="Senior">Senior</option>
            <option value="Lead">Lead</option>
            <option value="Executive">Executive</option>
          </select>
        </div>

        {/* Remote Type */}
        <div className="form-group" style={{ flex: '1', minWidth: '130px' }}>
          <label className="form-label">Remote Work</label>
          <select
            name="remote_type"
            value={filters.remote_type || ''}
            onChange={handleChange}
            className="select-control"
          >
            <option value="">All Modes</option>
            <option value="Remote">Remote</option>
            <option value="Hybrid">Hybrid</option>
            <option value="On-site">On-site</option>
          </select>
        </div>

        {/* Employment Type */}
        <div className="form-group" style={{ flex: '1', minWidth: '130px' }}>
          <label className="form-label">Contract Type</label>
          <select
            name="employment_type"
            value={filters.employment_type || ''}
            onChange={handleChange}
            className="select-control"
          >
            <option value="">All Contracts</option>
            <option value="Full-time">Full-time</option>
            <option value="Contract">Contract</option>
            <option value="Part-time">Part-time</option>
            <option value="Internship">Internship</option>
          </select>
        </div>
      </div>
    </div>
  );
};
