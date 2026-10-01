import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderGit2,
  Binary,
  Layers,
  Clock,
  ShieldCheck,
  FileCheck2,
} from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Dashboard', path: '/', icon: LayoutDashboard },
  { label: 'Cases', path: '/cases', icon: FolderGit2 },
  { label: 'Evidence Tree', path: '/evidence', icon: Layers },
  { label: 'Disk Map & Carve', path: '/disk-map', icon: Binary },
  { label: 'Multi-Camera Timeline', path: '/timeline', icon: Clock },
  { label: 'Custody Ledger', path: '/ledger', icon: ShieldCheck },
  { label: 'Sec 63 Reports', path: '/reports', icon: FileCheck2 },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950/70 p-4 flex flex-col justify-between shrink-0">
      <nav className="space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-slate-800 text-emerald-400 border border-slate-700/60 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-3 bg-slate-900/60 border border-slate-800/80 rounded-xl text-xs text-slate-400 space-y-1">
        <div className="font-semibold text-slate-300">NTRO SIH26150</div>
        <div className="text-[11px] text-slate-500">Forensic DVR/NVR Analysis Engine</div>
      </div>
    </aside>
  );
};
