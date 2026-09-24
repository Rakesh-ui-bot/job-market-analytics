import React, { useState, useEffect } from 'react';
import { Layers, Briefcase, DollarSign, Cpu, Globe, MapPin, Award } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, PieChart, Pie, Cell } from 'recharts';
import { getRoleDetail, getRoles } from '../services/api';
import { KpiCard } from '../components/KpiCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { formatCurrency, formatNumber, formatPercent } from '../utils/formatters';

const ROLE_OPTIONS = [
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'Data Scientist',
  'Data Analyst',
  'DevOps Engineer',
  'Android Developer',
  'QA Engineer',
];

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'];

export const RoleExplorer = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedRole, setSelectedRole] = useState('Frontend Developer');
  const [roleDetail, setRoleDetail] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getRoleDetail(selectedRole);
      setRoleDetail(res);
    } catch (err) {
      console.error('Failed to load role detail analytics:', err);
      setError('Failed to load role analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedRole]);

  if (loading && !roleDetail) return <LoadingSpinner text="Analyzing job role metrics & skill requirements..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div>
      {/* 1. Role Selector Card */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Single Role Deep-Dive Analytics</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Detailed benchmarking for required tech skills, compensation, experience tiers, and hiring cities.
            </p>
          </div>

          <div className="form-group" style={{ minWidth: '240px' }}>
            <label className="form-label">Select Target Role</label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="select-control"
            >
              {ROLE_OPTIONS.map((role) => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 2. Role KPI Cards */}
      <div className="grid-cols-4">
        <KpiCard
          title="Role Job Postings"
          value={formatNumber(roleDetail?.job_count)}
          subtitle="Total open positions"
          icon={Briefcase}
          badgeText="Demand"
          badgeColor="blue"
        />
        <KpiCard
          title="Remote Work Flexibility"
          value={formatPercent(roleDetail?.remote_percentage)}
          subtitle="Positions offering remote work"
          icon={Globe}
          badgeText="Flexible"
          badgeColor="green"
        />
        <KpiCard
          title="Avg Midpoint Salary"
          value={formatCurrency(roleDetail?.salary?.avg_midpoint)}
          subtitle={`Min: ${formatCurrency(roleDetail?.salary?.avg_min)} - Max: ${formatCurrency(roleDetail?.salary?.avg_max)}`}
          icon={DollarSign}
          badgeText="USD"
          badgeColor="warning"
        />
        <KpiCard
          title="Top Skill Required"
          value={roleDetail?.required_skills?.[0]?.skill_name || 'N/A'}
          subtitle={`${roleDetail?.required_skills?.[0]?.count || 0} job requests`}
          icon={Cpu}
          badgeText="Essential"
          badgeColor="purple"
        />
      </div>

      {/* 3. Role Charts Grid */}
      <div className="grid-cols-2">
        {/* Required Skills for Selected Role */}
        <div className="card">
          <div className="card-title">
            <span>Essential Skills for "{selectedRole}"</span>
            <Cpu size={18} color="var(--accent-primary)" />
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={roleDetail?.required_skills || []} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis type="number" />
                <YAxis dataKey="skill_name" type="category" width={90} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(val) => [`${val} jobs`, 'Required']} />
                <Bar dataKey="count" fill="var(--accent-primary)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Experience Level Distribution for Role */}
        <div className="card">
          <div className="card-title">
            <span>Experience Level Breakdown for "{selectedRole}"</span>
            <Award size={18} color="var(--accent-primary)" />
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={roleDetail?.experience_distribution || []}
                  dataKey="count"
                  nameKey="experience_level"
                  cx="50%"
                  cy="50%"
                  outerRadius={95}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {(roleDetail?.experience_distribution || []).map((entry, index) => (
                    <Cell key={`cell-exp-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(val) => [`${val} jobs`, 'Volume']} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Locations Hiring for Selected Role */}
        <div className="card">
          <div className="card-title">
            <span>Top Cities Hiring for "{selectedRole}"</span>
            <MapPin size={18} color="var(--accent-primary)" />
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={roleDetail?.top_locations || []}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="location_name" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={60} />
                <YAxis />
                <Tooltip formatter={(val) => [`${val} jobs`, 'City Volume']} />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Salary Benchmark Summary */}
        <div className="card">
          <div className="card-title">
            <span>Compensation Bounds Summary ($ USD)</span>
            <DollarSign size={18} color="var(--accent-primary)" />
          </div>
          <div style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Average Minimum Salary:</span>
              <strong style={{ fontSize: '1.1rem' }}>{formatCurrency(roleDetail?.salary?.avg_min)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Average Maximum Salary:</span>
              <strong style={{ fontSize: '1.1rem' }}>{formatCurrency(roleDetail?.salary?.avg_max)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Average Midpoint Salary:</span>
              <strong style={{ fontSize: '1.2rem', color: 'var(--accent-primary)' }}>{formatCurrency(roleDetail?.salary?.avg_midpoint)}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
