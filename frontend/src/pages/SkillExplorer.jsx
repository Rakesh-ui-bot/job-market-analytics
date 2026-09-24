import React, { useState, useEffect } from 'react';
import { Cpu, BarChart2, Briefcase, MapPin, DollarSign, Link as LinkIcon } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { getTopSkills, getSkillDetail } from '../services/api';
import { KpiCard } from '../components/KpiCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { formatCurrency, formatNumber, formatPercent } from '../utils/formatters';

const SKILL_OPTIONS = [
  'Python',
  'React',
  'Docker',
  'Git',
  'AWS',
  'SQL',
  'PostgreSQL',
  'TypeScript',
  'JavaScript',
  'Node.js',
  'FastAPI',
  'Django',
  'Pandas',
  'Kotlin',
  'Java',
  'C++',
];

export const SkillExplorer = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedSkill, setSelectedSkill] = useState('Python');
  const [topSkills, setTopSkills] = useState([]);
  const [skillDetail, setSkillDetail] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [topSkillsRes, detailRes] = await Promise.all([
        getTopSkills(15),
        getSkillDetail(selectedSkill),
      ]);
      setTopSkills(topSkillsRes);
      setSkillDetail(detailRes);
    } catch (err) {
      console.error('Failed to load skill explorer:', err);
      setError('Failed to load technology skill analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedSkill]);

  if (loading && !skillDetail) return <LoadingSpinner text="Analyzing technology skill demand & co-occurrences..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div>
      {/* 1. Skill Selector Card */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Single Technology Deep-Dive Analytics</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Explore demand, average compensation, top job roles, hiring cities, and co-occurring tech stack.
            </p>
          </div>

          <div className="form-group" style={{ minWidth: '220px' }}>
            <label className="form-label">Select Target Skill</label>
            <select
              value={selectedSkill}
              onChange={(e) => setSelectedSkill(e.target.value)}
              className="select-control"
            >
              {SKILL_OPTIONS.map((skill) => (
                <option key={skill} value={skill}>{skill}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 2. Skill KPI Cards */}
      <div className="grid-cols-4">
        <KpiCard
          title="Job Count"
          value={formatNumber(skillDetail?.job_count)}
          subtitle="Postings requiring skill"
          icon={Briefcase}
          badgeText="Demand"
          badgeColor="blue"
        />
        <KpiCard
          title="Market Penetration"
          value={formatPercent(skillDetail?.market_penetration_pct)}
          subtitle="Share of overall market"
          icon={Cpu}
          badgeText="Share"
          badgeColor="purple"
        />
        <KpiCard
          title="Average Salary"
          value={formatCurrency(skillDetail?.average_salary)}
          subtitle="Estimated midpoint compensation"
          icon={DollarSign}
          badgeText="USD"
          badgeColor="warning"
        />
        <KpiCard
          title="Top Co-occurring Skill"
          value={skillDetail?.related_skills?.[0]?.related_skill || 'N/A'}
          subtitle={`${skillDetail?.related_skills?.[0]?.co_occurrence_pct || 0}% co-occurrence`}
          icon={LinkIcon}
          badgeText="Related"
          badgeColor="green"
        />
      </div>

      {/* 3. Skill Detail Visualizations */}
      <div className="grid-cols-2">
        {/* Top Roles Requiring Selected Skill */}
        <div className="card">
          <div className="card-title">
            <span>Top Job Roles Requiring "{selectedSkill}"</span>
            <Briefcase size={18} color="var(--accent-primary)" />
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={skillDetail?.top_roles || []} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis type="number" />
                <YAxis dataKey="job_title" type="category" width={110} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(val) => [`${val} jobs`, 'Role Demand']} />
                <Bar dataKey="count" fill="var(--accent-primary)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Related Skills Co-occurrence Matrix */}
        <div className="card">
          <div className="card-title">
            <span>Frequently Co-occurring Skills with "{selectedSkill}"</span>
            <LinkIcon size={18} color="var(--accent-primary)" />
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={skillDetail?.related_skills || []} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis type="number" />
                <YAxis dataKey="related_skill" type="category" width={90} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(val, name, item) => [`${val} jobs (${item.payload.co_occurrence_pct}%)`, 'Co-occurrence']} />
                <Bar dataKey="co_occurrence_count" fill="#10b981" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Locations Hiring for Selected Skill */}
        <div className="card">
          <div className="card-title">
            <span>Top Hiring Cities for "{selectedSkill}"</span>
            <MapPin size={18} color="var(--accent-primary)" />
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={skillDetail?.top_locations || []}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="location_name" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={60} />
                <YAxis />
                <Tooltip formatter={(val) => [`${val} jobs`, 'City Hiring']} />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Overall Top Demanded Skills Benchmark */}
        <div className="card">
          <div className="card-title">
            <span>Overall Skill Market Ranking Benchmark</span>
            <BarChart2 size={18} color="var(--accent-primary)" />
          </div>
          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topSkills.slice(0, 8)} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis type="number" />
                <YAxis dataKey="skill_name" type="category" width={90} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(val) => [`${val} jobs`, 'Volume']} />
                <Bar dataKey="job_count" fill="#f59e0b" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
