import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, RefreshCw, ArrowRight } from 'lucide-react';
import { uploadCsv } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const DataUpload = () => {
  const [file, setFile] = useState(null);
  const [previewData, setPreviewData] = useState([]);
  const [headers, setHeaders] = useState([]);
  
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    if (!selectedFile.name.endsWith('.csv')) {
      setError('Invalid file type. Please select a valid .csv dataset file.');
      return;
    }

    setFile(selectedFile);
    setError(null);
    setResult(null);

    // Read preview
    const reader = new FileReader();
    reader.onload = (evt) => {
      const text = evt.target.result;
      const lines = text.split('\n').filter((l) => l.trim() !== '');
      if (lines.length > 0) {
        const cols = lines[0].split(',').map((c) => c.trim().replace(/^"/, '').replace(/"$/, ''));
        setHeaders(cols);
        
        const previewRows = lines.slice(1, 6).map((line) => {
          const vals = line.split(',').map((v) => v.trim().replace(/^"/, '').replace(/"$/, ''));
          const rowObj = {};
          cols.forEach((col, idx) => {
            rowObj[col] = vals[idx] || '';
          });
          return rowObj;
        });
        setPreviewData(previewRows);
      }
    };
    reader.readAsText(selectedFile.slice(0, 5000));
  };

  const handleUploadSubmit = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const res = await uploadCsv(file);
      setResult(res);
    } catch (err) {
      console.error('Upload failed:', err);
      const errMsg = err.response?.data?.detail || err.message || 'Failed to upload and process CSV file.';
      setError(errMsg);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      {/* Header Info */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="kpi-icon-wrapper">
            <Upload size={24} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Dataset Ingestion & ETL Pipeline</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Upload job postings CSV files. The pipeline automatically validates schema, removes duplicates, normalizes titles, extracts skills, and updates MySQL analytics.
            </p>
          </div>
        </div>
      </div>

      {/* Workflow Step Indicator */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem 1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
          <span style={{ color: file ? 'var(--accent-primary)' : 'inherit' }}>1. Select CSV File</span>
          <ArrowRight size={14} />
          <span style={{ color: previewData.length > 0 ? 'var(--accent-primary)' : 'inherit' }}>2. Validate Schema</span>
          <ArrowRight size={14} />
          <span style={{ color: uploading ? 'var(--accent-primary)' : 'inherit' }}>3. Clean & Extract Skills</span>
          <ArrowRight size={14} />
          <span style={{ color: result ? 'var(--success-text)' : 'inherit' }}>4. MySQL Ingestion</span>
        </div>
      </div>

      {/* Upload Drop Zone */}
      <div className="card" style={{ marginBottom: '1.5rem', textAlign: 'center', padding: '3rem 2rem' }}>
        <input
          type="file"
          id="csv-upload-input"
          accept=".csv"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <label htmlFor="csv-upload-input" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
          <div className="kpi-icon-wrapper" style={{ width: 64, height: 64 }}>
            <FileText size={32} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>{file ? file.name : 'Click to select CSV File'}</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              {file ? `${(file.size / 1024).toFixed(1)} KB` : 'Supports standard job postings CSV format'}
            </p>
          </div>
          <button type="button" className="btn btn-secondary" onClick={() => document.getElementById('csv-upload-input').click()}>
            Browse Files
          </button>
        </label>
      </div>

      {/* Validation Error Alert */}
      {error && (
        <div className="card" style={{ marginBottom: '1.5rem', borderColor: '#ef4444', backgroundColor: 'var(--bg-hover)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#ef4444' }}>
            <AlertCircle size={20} />
            <div>
              <strong>Validation / Processing Failure</strong>
              <div style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Preview Table & Ingestion Trigger */}
      {previewData.length > 0 && !result && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <div className="card-title">
            <span>CSV Dataset Validation Preview (First 5 Rows)</span>
            <span className="badge badge-green">Valid Schema</span>
          </div>
          <div className="table-container" style={{ marginBottom: '1.5rem' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  {headers.slice(0, 6).map((h, i) => (
                    <th key={i}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewData.map((row, idx) => (
                  <tr key={idx}>
                    {headers.slice(0, 6).map((h, i) => (
                      <td key={i}>{row[h]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button className="btn btn-primary" onClick={handleUploadSubmit} disabled={uploading}>
              {uploading ? (
                <span>Executing Pipeline...</span>
              ) : (
                <>
                  <Upload size={16} />
                  <span>Start ETL Pipeline & Ingest to Database</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Upload Execution Progress */}
      {uploading && <LoadingSpinner text="Running cleaner, skill extractor, and MySQL database ingestion..." />}

      {/* Ingestion Results Summary */}
      {result && (
        <div className="card" style={{ borderColor: 'var(--success-text)', backgroundColor: 'var(--bg-card)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', color: 'var(--success-text)' }}>
            <CheckCircle2 size={24} />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>ETL Ingestion Completed Successfully</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: 'var(--bg-hover)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>File Uploaded</div>
              <div style={{ fontWeight: 700 }}>{result.filename}</div>
            </div>
            <div style={{ background: 'var(--bg-hover)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Records Read</div>
              <div style={{ fontWeight: 700 }}>{result.records_read}</div>
            </div>
            <div style={{ background: 'var(--bg-hover)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Duplicates Removed</div>
              <div style={{ fontWeight: 700 }}>{result.duplicates_removed}</div>
            </div>
            <div style={{ background: 'var(--bg-hover)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Jobs Ingested</div>
              <div style={{ fontWeight: 700, color: 'var(--accent-primary)' }}>{result.jobs_inserted}</div>
            </div>
            <div style={{ background: 'var(--bg-hover)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Skills Extracted</div>
              <div style={{ fontWeight: 700, color: 'var(--success-text)' }}>{result.skills_extracted}</div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn btn-primary" onClick={() => { setFile(null); setPreviewData([]); setResult(null); }}>
              Upload Another File
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
