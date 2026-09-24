import React, { useEffect, useState } from 'react';
import {
  Briefcase,
  Building,
  MapPin,
  Cpu,
  Globe,
  DollarSign,
  BarChart2,
  PieChart as PieIcon,
  Layers
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  CartesianGrid
} from 'recharts';

import {
  getOverview,
  getTopSkills,
  getRoles,
  getLocations,
  getRemoteAnalytics,
  getSalaryAnalytics,
  getExperienceAnalytics
} from '../services/api';
import { useFilters } from '../context/FilterContext';
import { GlobalFilterBar } from '../components/GlobalFilterBar';
import { KpiCard } from '../components/KpiCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { formatCurrency, formatNumber, formatPercent } from '../utils/formatters';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#64748b'];

export const Dashboard = () => {
  const { filters } = useFilters();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [overview, setOverview] = useState(null);
  const [skills, setSkills] = useState([]);
  const [roles, setRoles] = useState([]);
  const [locations, setLocations] = useState([]);
  const [remote, setRemote] = useState([]);
  const [salaryRoles, setSalaryRoles] = useState([]);
  const [experience, setExperience] = useState([]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Pass active global filters to overview API
      const [
        overviewRes,
        skillsRes,
        rolesRes,
        locationsRes,
        remoteRes,
        salaryRes,
        expRes,
      ] = await Promise.all([
        getOverview(filters),
        getTopSkills(10),
        getRoles(10),
        getLocations(8),
        getRemoteAnalytics(),
        getSalaryAnalytics(),
        getExperienceAnalytics(),
      ]);

      setOverview(overviewRes);
      setSkills(skillsRes);
      setRoles(rolesRes);
      setLocations(locationsRes.cities || []);
      setRemote(remoteRes.distribution || []);
      setSalaryRoles(salaryRes.by_role || []);
      setExperience(expRes.distribution || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError(err.message || 'Failed to connect to backend server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  return (
    <div>
      {/* Interactive Global Filter Control Bar */}
      <GlobalFilterBar />

      {loading && !overview ? (
        <LoadingSpinner text="Computing filtered market metrics..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchData} />
      ) : (
        <>
          {/* 1. KPI Cards Row */}
          <div className="grid-cols-4">
            <KpiCard
              title="Filtered Jobs Volume"
              value={formatNumber(overview?.total_jobs)}
              subtitle="Matching job postings"
              icon={Briefcase}
              badgeText="Filtered"
              badgeColor="blue"
            />
            <KpiCard
              title="Hiring Employers"
              value={formatNumber(overview?.total_companies)}
              subtitle="Unique companies"
              icon={Building}
              badgeText="Verified"
              badgeColor="green"
            />
            <KpiCard
              title="Locations"
              value={formatNumber(overview?.total_locations)}
              subtitle="Cities & Countries"
              icon={MapPin}
              badgeText="Global"
              badgeColor="purple"
            />
            <KpiCard
              title="Unique Tech Skills"
              value={formatNumber(overview?.total_unique_skills)}
              subtitle="Tracked technologies"
              icon={Cpu}
              badgeText="Extracted"
              badgeColor="blue"
            />
            <KpiCard
              title="Remote Job Ratio"
              value={formatPercent(overview?.remote_job_percentage)}
              subtitle={`${formatNumber(overview?.remote_jobs_count)} Remote Positions`}
              icon={Globe}
              badgeText="Flexible"
              badgeColor="green"
            />
            <KpiCard
              title="Average Midpoint Salary"
              value={formatCurrency(overview?.average_salary?.midpoint)}
              subtitle={`Min: ${formatCurrency(overview?.average_salary?.min)} - Max: ${formatCurrency(overview?.average_salary?.max)}`}
              icon={DollarSign}
              badgeText="USD"
              badgeColor="warning"
            />
          </div>

          {/* 2. Charts Grid */}
          <div className="grid-cols-2">
            {/* Top Demanded Skills */}
            <div className="card">
              <div className="card-title">
                <span>Top Demanded Tech Skills</span>
                <BarChart2 size={18} color="var(--accent-primary)" />
              </div>
              <div style={{ height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={skills} layout="vertical" margin={{ left: 20, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis type="number" />
                    <YAxis dataKey="skill_name" type="category" width={90} tick={{ fontSize: 12 }} />
                    <Tooltip formatter={(val) => [`${val} jobs`, 'Demand']} />
                    <Bar dataKey="job_count" fill="var(--accent-primary)" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Jobs Distribution by Role */}
            <div className="card">
              <div className="card-title">
                <span>Jobs by Role Category</span>
                <Layers size={18} color="var(--accent-primary)" />
              </div>
              <div style={{ height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={roles.slice(0, 7)}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis dataKey="job_title" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={60} />
                    <YAxis />
                    <Tooltip formatter={(val) => [`${val} jobs`, 'Postings']} />
                    <Bar dataKey="job_count" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Salary Benchmark by Role */}
            <div className="card">
              <div className="card-title">
                <span>Average Salary by Role ($ USD)</span>
                <DollarSign size={18} color="var(--accent-primary)" />
              </div>
              <div style={{ height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={salaryRoles.slice(0, 7)} margin={{ bottom: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis dataKey="job_title" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" />
                    <YAxis tickFormatter={(v) => `$${v / 1000}k`} />
                    <Tooltip formatter={(val) => [formatCurrency(val), 'Avg Midpoint Salary']} />
                    <Bar dataKey="avg_midpoint_salary" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Remote Work Distribution */}
            <div className="card">
              <div className="card-title">
                <span>Remote Work Breakdown</span>
                <PieIcon size={18} color="var(--accent-primary)" />
              </div>
              <div style={{ height: 320, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={remote}
                      dataKey="job_count"
                      nameKey="remote_type"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      innerRadius={50}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                    >
                      {remote.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(val) => [`${val} jobs`, 'Volume']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
