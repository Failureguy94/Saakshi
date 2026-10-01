import React from 'react';
import { ShieldCheck, HardDrive } from 'lucide-react';
import { useCaseStore } from '../store/caseStore';

export const Navbar: React.FC = () => {
  const activeCase = useCaseStore((state) => state.activeCase);

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div>
          <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
            FrameProof
          </span>
          <span className="ml-2 text-xs text-slate-400 font-mono">v0.1.0-airgap</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {activeCase ? (
          <div className="flex items-center gap-2 bg-slate-800/60 border border-slate-700/60 rounded-full px-4 py-1.5 text-xs text-slate-200">
            <HardDrive className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-semibold">{activeCase.case_number}</span>
            <span className="text-slate-400">({activeCase.title})</span>
          </div>
        ) : (
          <span className="text-xs text-slate-500 italic">No Active Case Selected</span>
        )}

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          AIR-GAPPED
        </div>
      </div>
    </header>
  );
};
