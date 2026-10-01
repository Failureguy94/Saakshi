import React from 'react';
import { Clock, Video, Sliders } from 'lucide-react';

export const MultiCameraTimeline: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-emerald-400" />
            Multi-Camera Timeline Synchronization
          </h1>
          <p className="text-sm text-slate-400">
            Harmonize disparate DVR camera angles with RTC drift compensation and visual OSD OCR.
          </p>
        </div>
      </div>

      {/* Video Multi-Pane Grid Placeholder (Video.js Ready) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((ch) => (
          <div
            key={ch}
            className="aspect-video bg-slate-950 rounded-xl border border-slate-800 flex flex-col items-center justify-center p-4 relative group"
          >
            <div className="absolute top-3 left-3 text-xs font-mono bg-slate-900/80 px-2 py-1 rounded border border-slate-700/60 text-slate-300">
              CH-0{ch} • Camera Feed
            </div>
            <Video className="w-8 h-8 text-slate-700 group-hover:text-slate-500 transition-colors" />
            <span className="text-xs text-slate-500 mt-2 font-mono">Video.js Player Mount Point</span>
          </div>
        ))}
      </div>

      {/* Synchronized Timeline Scrubber Shell */}
      <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span className="font-semibold text-slate-300">Harmonized UTC Baseline: </span>
            <span className="font-mono text-emerald-400">2026-10-01 12:00:00 UTC (Drift: ±0.0s)</span>
          </div>
          <span className="text-slate-500">Multi-Channel Scrubber</span>
        </div>

        <div className="h-10 bg-slate-950 border border-slate-800 rounded-lg relative overflow-hidden flex items-center px-4">
          <div className="w-1 h-full bg-emerald-400 absolute left-1/3 shadow-[0_0_8px_#34d399]" />
          <div className="text-xs text-slate-600 font-mono">Multi-Camera Synced Track (Playback Scrubber Shell)</div>
        </div>
      </div>
    </div>
  );
};
