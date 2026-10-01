import React from 'react';
import { Binary, Play, Cpu } from 'lucide-react';

export const DiskMap: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Binary className="w-5 h-5 text-emerald-400" />
            Disk Map & Sector Carving
          </h1>
          <p className="text-sm text-slate-400">
            Interactive sector allocation map and Annex-B H.264/H.265 NAL start code carver.
          </p>
        </div>

        <button
          disabled
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 text-slate-500 text-sm font-semibold cursor-not-allowed"
        >
          <Play className="w-4 h-4" />
          Start Annex-B Carve (Planned)
        </button>
      </div>

      <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Physical Sector Allocation Grid</span>
          <span>512 Bytes / Sector • 64KB Clusters</span>
        </div>

        {/* Mock sector grid representation */}
        <div className="grid grid-cols-16 gap-1 p-4 bg-slate-950 rounded-xl border border-slate-800/80">
          {Array.from({ length: 64 }).map((_, i) => (
            <div
              key={i}
              className={`h-4 rounded-sm transition-colors ${
                i % 7 === 0
                  ? 'bg-emerald-500/80 hover:bg-emerald-400'
                  : i % 11 === 0
                  ? 'bg-cyan-500/80 hover:bg-cyan-400'
                  : 'bg-slate-800/60 hover:bg-slate-700'
              }`}
              title={`Cluster ${i}: ${i % 7 === 0 ? 'NAL Start Code' : 'Unallocated Slack'}`}
            />
          ))}
        </div>

        <div className="flex items-center gap-6 pt-2 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm bg-emerald-500/80"></span>
            <span>H.264 / H.265 NAL Units</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm bg-cyan-500/80"></span>
            <span>Indexed Superblock</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-sm bg-slate-800/60"></span>
            <span>Unallocated Slack</span>
          </div>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3 text-xs text-slate-400">
        <Cpu className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-300">Annex-B Streaming Engine: </span>
          The core NAL carver is implemented in <code className="text-emerald-400">recovery/nal_carver.py</code> with a drop-in abstract interface for Rust acceleration. Real-time sector visualization will be wired to the background worker.
        </div>
      </div>
    </div>
  );
};
