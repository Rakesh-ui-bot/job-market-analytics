import React from 'react';
import { MapPin, Building, DollarSign, Calendar, Globe, Award } from 'lucide-react';
import { formatCurrency, formatDate } from '../utils/formatters';

export const JobCard = ({ job, onClick }) => {
  const getBadgeColor = (remoteType) => {
    if (!remoteType) return 'blue';
    const type = remoteType.toLowerCase();
    if (type.includes('remote')) return 'green';
    if (type.includes('hybrid')) return 'purple';
    return 'warning';
  };

  return (
    <div className="card" onClick={onClick} style={{ cursor: onClick ? 'pointer' : 'default' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{job.job_title}</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            <Building size={14} />
            <span>{job.company}</span>
          </div>
        </div>

        <span className={`badge badge-${getBadgeColor(job.remote_type)}`}>
          {job.remote_type}
        </span>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', margin: '0.75rem 0', fontSize: '0.825rem', color: 'var(--text-secondary)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <MapPin size={14} />
          <span>{job.location}, {job.country}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <DollarSign size={14} />
          <span>
            {formatCurrency(job.salary_min)} - {formatCurrency(job.salary_max)}
            {job.salary_is_imputed && <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginLeft: '4px' }}>(Imputed)</span>}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Award size={14} />
          <span>{job.experience_level}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Calendar size={14} />
          <span>{formatDate(job.posting_date)}</span>
        </div>
      </div>

      {job.skills && job.skills.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '1rem' }}>
          {job.skills.map((skill, i) => (
            <span
              key={i}
              style={{
                fontSize: '0.75rem',
                padding: '0.2rem 0.5rem',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-hover)',
                color: 'var(--text-secondary)',
                fontWeight: 500,
              }}
            >
              {skill}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
