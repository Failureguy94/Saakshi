import React from 'react';
import { Layers, HardDrive, Camera, Film } from 'lucide-react';
import { useCaseStore } from '../store/caseStore';

export const EvidenceTree: React.FC = () => {
  const activeCase = useCaseStore((state) => state.activeCase);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-emerald-400" />
            Unified Evidence Hierarchy
          </h1>
          <p className="text-sm text-slate-400">
            Hierarchical mapping: Case → Device → EvidenceImage → Volume → Channel → Segment → Frame
          </p>
        </div>
      </div>

      <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800 text-center space-y-4">
        <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center mx-auto text-emerald-400">
          <HardDrive className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-base font-semibold text-slate-200">
            {activeCase ? `Evidence Tree for ${activeCase.case_number}` : 'No Case Selected'}
          </h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
            Connect an acquired raw disk image (.raw, .dd, .E01) or select a case to view parsed partitions, camera channels, and carved video segments.
          </p>
        </div>

        <div className="flex items-center justify-center gap-6 pt-4 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-cyan-400" /> Devices (0)
          </div>
          <div className="flex items-center gap-2">
            <Camera className="w-4 h-4 text-indigo-400" /> Channels (0)
          </div>
          <div className="flex items-center gap-2">
            <Film className="w-4 h-4 text-amber-400" /> Carved Segments (0)
          </div>
        </div>
      </div>
    </div>
  );
};
