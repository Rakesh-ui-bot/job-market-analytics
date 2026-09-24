import React, { useState } from 'react';
import { Target, CheckCircle2, AlertCircle, Cpu, Info, Plus, X } from 'lucide-react';
import { analyzeSkillGap } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

const ROLE_OPTIONS = [
  'Frontend Developer',
  'React Developer',
  'Python Developer',
  'Data Analyst',
  'Software Engineer',
  'Android Developer',
  'Backend Developer',
  'Data Scientist',
  'DevOps Engineer',
  'QA Engineer',
];

const PRESET_SKILLS = [
  'Python', 'JavaScript', 'TypeScript', 'React', 'HTML', 'CSS',
  'SQL', 'PostgreSQL', 'MySQL', 'Node.js', 'FastAPI', 'Django',
  'AWS', 'Docker', 'Git', 'GitHub', 'Pandas', 'NumPy', 'Tableau',
];

export const SkillGapAnalyzer = () => {
  const [targetRole, setTargetRole] = useState('Python Developer');
  const [userSkills, setUserSkills] = useState(['Python', 'Git', 'SQL']);
  const [customInput, setCustomInput] = useState('');

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAddSkill = (skillToAdd) => {
    const clean = skillToAdd.strip ? skillToAdd.strip() : skillToAdd.trim();
    if (!clean) return;
    if (!userSkills.includes(clean)) {
      setUserSkills([...userSkills, clean]);
    }
    setCustomInput('');
  };

  const handleRemoveSkill = (skillToRemove) => {
    setUserSkills(userSkills.filter((s) => s !== skillToRemove));
  };

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const res = await analyzeSkillGap(targetRole, userSkills);
      setResult(res);
    } catch (err) {
      console.error('Skill gap analysis failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* 1. Header & Disclaimer Banner */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
          <div className="kpi-icon-wrapper">
            <Target size={24} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Career Skill Gap Analyzer</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Self-assessment tool comparing your current tech skills against technologies commonly required in target job postings.
            </p>
          </div>
        </div>

        {/* Disclaimer Alert Banner */}
        <div
          style={{
            padding: '0.85rem 1.25rem',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--bg-hover)',
            border: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.75rem',
            fontSize: '0.85rem',
            color: 'var(--text-secondary)',
          }}
        >
          <Info size={18} color="var(--accent-primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Educational Self-Assessment Tool:</strong> This feature performs a purely descriptive comparison of tech skills against job market data. It does not predict hiring probability, interview outcomes, or guarantee employment placement.
          </div>
        </div>
      </div>

      {/* 2. Target Role & Current Skills Inputs */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="grid-cols-2">
          {/* Target Role Selector */}
          <div className="form-group">
            <label className="form-label">1. Select Target Career Role</label>
            <select
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="select-control"
            >
              {ROLE_OPTIONS.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          {/* Custom Skill Input */}
          <div className="form-group">
            <label className="form-label">2. Add Custom Skill</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                value={customInput}
                onChange={(e) => setCustomInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddSkill(customInput)}
                placeholder="Type skill e.g. Docker, Redis"
                className="input-control"
              />
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => handleAddSkill(customInput)}
              >
                <Plus size={16} />
                <span>Add</span>
              </button>
            </div>
          </div>
        </div>

        {/* Quick Add Presets */}
        <div style={{ marginTop: '1rem' }}>
          <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block' }}>Quick Add Common Skills:</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {PRESET_SKILLS.map((skill) => {
              const isSelected = userSkills.includes(skill);
              return (
                <button
                  key={skill}
                  type="button"
                  onClick={() => (isSelected ? handleRemoveSkill(skill) : handleAddSkill(skill))}
                  style={{
                    fontSize: '0.75rem',
                    padding: '0.25rem 0.6rem',
                    borderRadius: 'var(--radius-full)',
                    border: '1px solid var(--border-color)',
                    backgroundColor: isSelected ? 'var(--accent-primary)' : 'var(--bg-hover)',
                    color: isSelected ? '#fff' : 'var(--text-primary)',
                    cursor: 'pointer',
                    fontWeight: 500,
                  }}
                >
                  {isSelected ? `✓ ${skill}` : `+ ${skill}`}
                </button>
              );
            })}
          </div>
        </div>

        {/* Active Selected User Skills Pills */}
        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <label className="form-label">Your Active Skills ({userSkills.length}):</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
            {userSkills.map((skill) => (
              <span key={skill} className="badge badge-blue" style={{ padding: '0.35rem 0.75rem', fontSize: '0.85rem', gap: '0.35rem' }}>
                {skill}
                <X
                  size={14}
                  style={{ cursor: 'pointer', marginLeft: '4px' }}
                  onClick={() => handleRemoveSkill(skill)}
                />
              </span>
            ))}
          </div>
        </div>

        {/* Submit Action */}
        <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn btn-primary" onClick={handleAnalyze} disabled={loading || userSkills.length === 0}>
            <Target size={16} />
            <span>Analyze Skill Gap</span>
          </button>
        </div>
      </div>

      {/* 3. Loading State */}
      {loading && <LoadingSpinner text="Comparing your skills against job posting requirements..." />}

      {/* 4. Results Breakdown */}
      {result && !loading && (
        <div className="grid-cols-2">
          {/* Matching Skills */}
          <div className="card">
            <div className="card-title" style={{ color: 'var(--success-text)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle2 size={20} />
                <span>Matching Skills ({result.matching_skills.length})</span>
              </div>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Skills you currently possess that are actively required for {result.target_role} roles.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {result.matching_skills.length === 0 ? (
                <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No matching skills found for this role.</span>
              ) : (
                result.matching_skills.map((skill) => (
                  <span key={skill} className="badge badge-green" style={{ padding: '0.4rem 0.8rem', fontSize: '0.875rem' }}>
                    ✓ {skill}
                  </span>
                ))
              )}
            </div>
          </div>

          {/* Missing Skills */}
          <div className="card">
            <div className="card-title" style={{ color: 'var(--warning-text)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertCircle size={20} />
                <span>Missing Skills ({result.missing_skills.length})</span>
              </div>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Technologies required in market job postings for {result.target_role} that are not in your profile.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {result.missing_skills.map((skill) => (
                <span key={skill} className="badge badge-warning" style={{ padding: '0.4rem 0.8rem', fontSize: '0.875rem' }}>
                  + {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Related / Complementary Skills */}
          <div className="card" style={{ gridColumn: 'span 2' }}>
            <div className="card-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Cpu size={20} color="var(--accent-primary)" />
                <span>Recommended Complementary Tech Stack</span>
              </div>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Technologies frequently paired with your existing matching skills in job postings.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {result.related_skills.map((skill) => (
                <span key={skill} className="badge badge-purple" style={{ padding: '0.4rem 0.8rem', fontSize: '0.875rem' }}>
                  ★ {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
