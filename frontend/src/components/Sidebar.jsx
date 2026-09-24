import React from 'react';
import { LayoutDashboard, Briefcase, Cpu, Layers, Upload, Target } from 'lucide-react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'jobs', label: 'Jobs Search', icon: Briefcase },
  { id: 'skills', label: 'Skill Explorer', icon: Cpu },
  { id: 'roles', label: 'Role Explorer', icon: Layers },
  { id: 'gap', label: 'Skill Gap Analyzer', icon: Target },
  { id: 'upload', label: 'Data Ingestion', icon: Upload },
];

export const Sidebar = ({ activeTab, setActiveTab }) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div style={{ background: 'var(--accent-primary)', padding: '6px', borderRadius: '8px', color: '#fff' }}>
          <Briefcase size={22} />
        </div>
        <div>
          <div className="sidebar-brand">Job Analytics</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Market & Skill Demand</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={{ padding: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        <div>FastAPI & MySQL Backend</div>
        <div style={{ marginTop: '0.25rem' }}>100% Dynamic Real Data</div>
      </div>
    </aside>
  );
};
