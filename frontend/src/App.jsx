import React, { useState } from 'react';
import { useTheme } from './hooks/useTheme';
import { FilterProvider } from './context/FilterContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { Jobs } from './pages/Jobs';
import { SkillExplorer } from './pages/SkillExplorer';
import { RoleExplorer } from './pages/RoleExplorer';
import { SkillGapAnalyzer } from './pages/SkillGapAnalyzer';
import { DataUpload } from './pages/DataUpload';

export function AppContent() {
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('dashboard');

  const getPageTitle = () => {
    switch (activeTab) {
      case 'dashboard':
        return 'Job Market Analytics Overview';
      case 'jobs':
        return 'Tech Job Postings Search';
      case 'skills':
        return 'Technology Skill Demand Explorer';
      case 'roles':
        return 'Software & Data Role Benchmark';
      case 'gap':
        return 'Career Skill Gap Self-Assessment';
      case 'upload':
        return 'Dataset Upload & Ingestion Pipeline';
      default:
        return 'Job Market Analytics';
    }
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'jobs':
        return <Jobs />;
      case 'skills':
        return <SkillExplorer />;
      case 'roles':
        return <RoleExplorer />;
      case 'gap':
        return <SkillGapAnalyzer />;
      case 'upload':
        return <DataUpload />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="main-content">
        <Header title={getPageTitle()} theme={theme} toggleTheme={toggleTheme} />
        <main className="page-container">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
}

export function App() {
  return (
    <FilterProvider>
      <AppContent />
    </FilterProvider>
  );
}

export default App;
