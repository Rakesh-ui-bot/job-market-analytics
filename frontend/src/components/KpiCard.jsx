import React from 'react';

export const KpiCard = ({ title, value, subtitle, icon: Icon, badgeText, badgeColor = 'blue' }) => {
  return (
    <div className="card kpi-card">
      <div>
        <div className="kpi-label">{title}</div>
        <div className="kpi-value">{value}</div>
        {subtitle && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>{subtitle}</div>}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
        {Icon && (
          <div className="kpi-icon-wrapper">
            <Icon size={22} />
          </div>
        )}
        {badgeText && <span className={`badge badge-${badgeColor}`}>{badgeText}</span>}
      </div>
    </div>
  );
};
