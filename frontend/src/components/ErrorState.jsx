import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const ErrorState = ({ message = "Failed to load data from backend server.", onRetry }) => {
  return (
    <div className="state-container card" style={{ maxWidth: '500px', margin: '2rem auto' }}>
      <AlertCircle size={40} color="#ef4444" />
      <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Error Loading Analytics</h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{message}</p>
      {onRetry && (
        <button className="btn btn-primary" onClick={onRetry} style={{ marginTop: '0.5rem' }}>
          <RefreshCw size={16} />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
};
