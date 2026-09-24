import React from 'react';

export const LoadingSpinner = ({ text = "Loading analytics data..." }) => {
  return (
    <div className="state-container">
      <div className="spinner"></div>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>{text}</p>
    </div>
  );
};
