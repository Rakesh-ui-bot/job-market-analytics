import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, X, Briefcase, Search, ArrowUpDown, Filter, RotateCcw } from 'lucide-react';
import { getJobs, getJobById } from '../services/api';
import { useFilters } from '../context/FilterContext';
import { GlobalFilterBar } from '../components/GlobalFilterBar';
import { JobCard } from '../components/JobCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { formatCurrency, formatDate } from '../utils/formatters';

export const Jobs = () => {
  const { filters, setFilter, resetFilters } = useFilters();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(12);
  const [sortBy, setSortBy] = useState('newest'); // 'newest' | 'salary_desc' | 'salary_asc'

  const [data, setData] = useState({ items: [], total: 0, pages: 1 });
  const [selectedJob, setSelectedJob] = useState(null);

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getJobs({ ...filters, page, limit });
      
      // Client side sorting for fetched list
      let sortedItems = [...res.items];
      if (sortBy === 'salary_desc') {
        sortedItems.sort((a, b) => (b.salary_max || 0) - (a.salary_max || 0));
      } else if (sortBy === 'salary_asc') {
        sortedItems.sort((a, b) => (a.salary_min || 0) - (b.salary_min || 0));
      } else {
        // newest
        sortedItems.sort((a, b) => new Date(b.posting_date) - new Date(a.posting_date));
      }

      setData({ ...res, items: sortedItems });
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
      setError(err.message || 'Failed to load job listings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [filters, page, limit, sortBy]);

  const handleJobClick = async (jobId) => {
    try {
      const fullJob = await getJobById(jobId);
      setSelectedJob(fullJob);
    } catch (err) {
      console.error('Failed to fetch job detail:', err);
    }
  };

  return (
    <div>
      {/* 1. Global Interactive Filter Bar */}
      <GlobalFilterBar />

      {/* 2. Controls Header: Sorting & Items per page */}
      <div className="card" style={{ padding: '1rem 1.5rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          Showing <strong>{data.items.length}</strong> of <strong>{data.total.toLocaleString()}</strong> matching positions
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Sorting Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ArrowUpDown size={16} color="var(--text-muted)" />
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="select-control"
              style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}
            >
              <option value="newest">Newest First</option>
              <option value="salary_desc">Salary: High to Low</option>
              <option value="salary_asc">Salary: Low to High</option>
            </select>
          </div>

          {/* Page Limit Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Per Page:</span>
            <select
              value={limit}
              onChange={(e) => {
                setLimit(Number(e.target.value));
                setPage(1);
              }}
              className="select-control"
              style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}
            >
              <option value={12}>12</option>
              <option value={24}>24</option>
              <option value={48}>48</option>
            </select>
          </div>
        </div>
      </div>

      {/* 3. Job Listings Grid */}
      {loading ? (
        <LoadingSpinner text="Searching active job postings..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchJobs} />
      ) : data.items.length === 0 ? (
        <div className="card state-container" style={{ padding: '4rem 2rem' }}>
          <Briefcase size={48} color="var(--text-muted)" />
          <h3>No Job Postings Found</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            No active postings matched your filter criteria. Try resetting or adjusting filters.
          </p>
          <button className="btn btn-primary" onClick={resetFilters} style={{ marginTop: '0.5rem' }}>
            Reset All Filters
          </button>
        </div>
      ) : (
        <div className="grid-cols-2">
          {data.items.map((job) => (
            <JobCard key={job.id} job={job} onClick={() => handleJobClick(job.id)} />
          ))}
        </div>
      )}

      {/* 4. Pagination Bar */}
      {data.pages > 1 && (
        <div className="pagination">
          <div className="pagination-info">
            Page {data.page} of {data.pages}
          </div>
          <div className="pagination-controls">
            <button
              className="btn btn-secondary"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              <ChevronLeft size={16} />
              <span>Previous</span>
            </button>
            <button
              className="btn btn-secondary"
              disabled={page >= data.pages}
              onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
            >
              <span>Next</span>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* 5. Job Detail Modal */}
      {selectedJob && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '1.5rem',
          }}
          onClick={() => setSelectedJob(null)}
        >
          <div
            className="card"
            style={{
              maxWidth: '700px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              position: 'relative',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setSelectedJob(null)}
              style={{
                position: 'absolute',
                top: '1rem',
                right: '1rem',
                background: 'none',
                border: 'none',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
              }}
            >
              <X size={20} />
            </button>

            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.25rem' }}>
              {selectedJob.job_title}
            </h2>
            <div style={{ color: 'var(--accent-primary)', fontWeight: 600, fontSize: '1rem', marginBottom: '1rem' }}>
              {selectedJob.company?.name || selectedJob.company}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
              <div><strong>Location:</strong> {selectedJob.location?.location_name || selectedJob.location}, {selectedJob.location?.country || selectedJob.country}</div>
              <div><strong>Work Flexibility:</strong> {selectedJob.remote_type}</div>
              <div><strong>Employment Type:</strong> {selectedJob.employment_type}</div>
              <div><strong>Experience Level:</strong> {selectedJob.experience_level}</div>
              <div><strong>Salary Bounds:</strong> {formatCurrency(selectedJob.salary_min)} - {formatCurrency(selectedJob.salary_max)}</div>
              <div><strong>Education:</strong> {selectedJob.education}</div>
              <div><strong>Posting Date:</strong> {formatDate(selectedJob.posting_date)}</div>
              <div><strong>Job Identifier:</strong> {selectedJob.job_id}</div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.5rem' }}>Required Tech Skills</h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {selectedJob.skills?.map((skill, idx) => (
                  <span key={idx} className="badge badge-blue">
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.5rem' }}>Job Description</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                {selectedJob.description}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
