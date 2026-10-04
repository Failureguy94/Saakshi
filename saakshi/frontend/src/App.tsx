import React, { useEffect } from 'react';
import { Activity, Database, FileText, Search, Shield, Clock, LayoutDashboard, Settings } from 'lucide-react';
import { useStore } from './store';
import Pipeline from './pages/Pipeline';
import Evidence from './pages/Evidence';
import Recovery from './pages/Recovery';
import Timeline from './pages/Timeline';
import Integrity from './pages/Integrity';
import Report from './pages/Report';

const PAGES = [
  { name: 'Pipeline', icon: LayoutDashboard },
  { name: 'Evidence', icon: FileText },
  { name: 'Recovery', icon: Search },
  { name: 'Timeline', icon: Clock },
  { name: 'Integrity', icon: Shield },
  { name: 'Report', icon: Database },
];

export default function App() {
  const { currentPage, setCurrentPage, caseInfo, setCaseInfo } = useStore();

  useEffect(() => {
    fetch('http://localhost:8000/api/case')
      .then(res => res.json())
      .then(data => setCaseInfo(data))
      .catch(console.error);
  }, []);

  const resetPipeline = async () => {
    if (confirm("Reset the entire pipeline?")) {
      await fetch('http://localhost:8000/api/reset', { method: 'POST' });
      window.location.reload();
    }
  };

  return (
    <div className="flex h-screen bg-bg text-text font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-surface border-r border-border flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-border">
          <Activity className="w-6 h-6 text-accent mr-3" />
          <span className="font-bold text-lg tracking-wide">Saakshi</span>
        </div>
        <div className="flex-1 py-4 flex flex-col gap-2 px-4">
          {PAGES.map(page => {
            const Icon = page.icon;
            const active = currentPage === page.name;
            return (
              <button
                key={page.name}
                onClick={() => setCurrentPage(page.name)}
                className={`flex items-center px-4 py-3 rounded-xl transition-all duration-200 ${
                  active ? 'bg-indigo/20 text-indigo border border-indigo/30' : 'text-muted hover:bg-white/5 hover:text-text'
                }`}
              >
                <Icon className="w-5 h-5 mr-3" strokeWidth={active ? 2.5 : 1.5} />
                <span className="font-medium">{page.name}</span>
              </button>
            );
          })}
        </div>
        <div className="p-4 border-t border-border">
          <button 
            onClick={resetPipeline}
            className="w-full flex items-center px-4 py-3 text-danger/80 hover:bg-danger/10 hover:text-danger rounded-xl transition-colors"
          >
            <Settings className="w-5 h-5 mr-3" />
            <span>Reset Demo</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 border-b border-border bg-surface/50 backdrop-blur flex items-center px-8 justify-between shrink-0">
          <h1 className="text-xl font-semibold">{currentPage}</h1>
          <div className="flex items-center space-x-4">
            {caseInfo && caseInfo.size > 0 ? (
              <div className="flex items-center space-x-3 bg-surface px-4 py-1.5 rounded-full border border-border">
                <span className="text-sm text-muted">Case ID:</span>
                <span className="text-sm font-mono text-accent">SAAKSHI-DEMO-001</span>
                <div className="w-px h-4 bg-border mx-2" />
                <div className="flex items-center text-xs">
                  <div className="w-2 h-2 rounded-full bg-success mr-2" />
                  <span className="text-success">Active</span>
                </div>
              </div>
            ) : (
              <div className="flex items-center space-x-3 bg-surface px-4 py-1.5 rounded-full border border-border text-warning text-sm">
                No active case (Generate Image)
              </div>
            )}
          </div>
        </header>

        {/* Page Container */}
        <main className="flex-1 overflow-auto p-8 relative">
          {currentPage === 'Pipeline' && <Pipeline />}
          {currentPage === 'Evidence' && <Evidence />}
          {currentPage === 'Recovery' && <Recovery />}
          {currentPage === 'Timeline' && <Timeline />}
          {currentPage === 'Integrity' && <Integrity />}
          {currentPage === 'Report' && <Report />}
        </main>
      </div>
    </div>
  );
}
