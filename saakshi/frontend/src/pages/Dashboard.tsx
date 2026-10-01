import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchHealth, fetchCases } from '../api/client';
import { ShieldAlert, Activity, CheckCircle2, FolderOpen, HardDrive, KeyRound } from 'lucide-react';
import { useCaseStore } from '../store/caseStore';

export const Dashboard: React.FC = () => {
  const setActiveCase = useCaseStore((state) => state.setActiveCase);

  const { data: health, isLoading: healthLoading, error: healthError } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 10000,
  });

  const { data: cases, isLoading: casesLoading } = useQuery({
    queryKey: ['cases'],
    queryFn: fetchCases,
  });

  return (
    <div className="space-y-6">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Forensic Control Center</h1>
          <p className="text-sm text-slate-400 mt-1">
            Vendor-Agnostic Surveillance DVR/NVR Reconstruction & Integrity Engine (NTRO / SIH26150)
          </p>
        </div>

        <div className="flex items-center gap-3">
          {healthLoading ? (
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Activity className="w-4 h-4 animate-spin text-cyan-400" />
              Checking Engine Status...
            </div>
          ) : healthError ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-950/50 border border-red-500/40 text-red-300 text-xs font-mono">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              Engine Offline
            </div>
          ) : (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs font-mono">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Engine Online ({health?.version})
            </div>
          )}
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Air-Gapped Mode</span>
            <KeyRound className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl font-bold text-slate-100">
            {health?.offline_mode ? 'Enforced' : 'Disabled'}
          </div>
          <div className="text-xs text-emerald-500 font-mono">Zero external connections</div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Active Cases</span>
            <FolderOpen className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-xl font-bold text-slate-100">
            {casesLoading ? '...' : cases?.length || 0}
          </div>
          <div className="text-xs text-slate-400">Registered investigation files</div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">OEM Profiles</span>
            <HardDrive className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-xl font-bold text-slate-100">9 Profiles</div>
          <div className="text-xs text-slate-400">Hikvision, Dahua, CP Plus + 6</div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/50 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Legal Standard</span>
            <CheckCircle2 className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-xl font-bold text-slate-100">Sec 63 BSA</div>
          <div className="text-xs text-slate-400">Section 65B IEA Compliant</div>
        </div>
      </div>

      {/* Cases Overview Table */}
      <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-200">Recent Investigation Cases</h2>
          <span className="text-xs text-slate-400">Persistent SQLite/PostgreSQL storage</span>
        </div>

        {casesLoading ? (
          <div className="p-8 text-center text-sm text-slate-500">Loading cases...</div>
        ) : !cases || cases.length === 0 ? (
          <div className="p-12 text-center border border-dashed border-slate-800 rounded-xl space-y-3">
            <FolderOpen className="w-8 h-8 text-slate-600 mx-auto" />
            <div className="text-sm text-slate-400">No forensic cases registered yet.</div>
            <div className="text-xs text-slate-500">Navigate to the Cases tab to initialize your first investigation.</div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-slate-950/60 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Case Number</th>
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4">Investigator</th>
                  <th className="py-3 px-4">Agency</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {cases.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-emerald-400">{c.case_number}</td>
                    <td className="py-3 px-4 text-slate-200">{c.title}</td>
                    <td className="py-3 px-4">{c.investigator_name}</td>
                    <td className="py-3 px-4 text-slate-400">{c.agency}</td>
                    <td className="py-3 px-4">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-950/60 border border-emerald-500/30 text-emerald-400">
                        {c.status}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => setActiveCase(c)}
                        className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 underline"
                      >
                        Select Case
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
