import React, { useEffect, useState, useRef } from 'react';
import { Card } from '../components/Card';
import { PlayCircle } from 'lucide-react';
import { useStore } from '../store';

interface Segment {
  id: number;
  channel: number;
  offset: number;
  length: number;
  source: string;
  confidence: number;
  dvr_time: string;
  normalized_time: string;
  file_hash: string;
}

export default function Recovery() {
  const [segments, setSegments] = useState<Segment[]>([]);
  const [selectedSeg, setSelectedSeg] = useState<Segment | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { caseInfo } = useStore();

  useEffect(() => {
    fetch('http://localhost:8000/api/segments')
      .then(r => r.json())
      .then(d => setSegments(d.segments || []));
  }, []);

  useEffect(() => {
    if (!canvasRef.current || !caseInfo) return;
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;
    
    const w = canvasRef.current.width;
    const h = canvasRef.current.height;
    ctx.clearRect(0, 0, w, h);
    
    // Draw base unallocated
    ctx.fillStyle = '#1e293b'; // border color roughly
    ctx.fillRect(0, 0, w, h);
    
    // Draw header
    ctx.fillStyle = '#6366F1'; // indigo
    ctx.fillRect(0, 0, Math.max(2, (512 / caseInfo.size) * w), h);
    
    // Draw index
    ctx.fillStyle = '#F59E0B'; // warning
    ctx.fillRect((512 / caseInfo.size) * w, 0, Math.max(2, (10240 / caseInfo.size) * w), h);
    
    // Draw segments
    segments.forEach(seg => {
      const x = (seg.offset / caseInfo.size) * w;
      const sw = (seg.length / caseInfo.size) * w;
      ctx.fillStyle = seg.source === 'indexed' ? '#2DD4BF' : '#22C55E';
      ctx.fillRect(x, 0, Math.max(1, sw), h);
    });
  }, [segments, caseInfo]);

  return (
    <div className="h-full flex flex-col gap-6">
      <Card title="Disk Image Map" className="shrink-0 h-32">
        <div className="relative w-full h-8 mt-2 rounded overflow-hidden">
          <canvas ref={canvasRef} width={1000} height={32} className="w-full h-full" />
        </div>
        <div className="flex space-x-6 mt-4 text-xs">
          <div className="flex items-center"><div className="w-3 h-3 bg-indigo rounded mr-2" /> Header</div>
          <div className="flex items-center"><div className="w-3 h-3 bg-warning rounded mr-2" /> Index Table</div>
          <div className="flex items-center"><div className="w-3 h-3 bg-accent rounded mr-2" /> Indexed Segment</div>
          <div className="flex items-center"><div className="w-3 h-3 bg-success rounded mr-2" /> Recovered/Deleted</div>
          <div className="flex items-center"><div className="w-3 h-3 bg-[#1e293b] border border-border rounded mr-2" /> Unallocated</div>
        </div>
      </Card>

      <div className="flex-1 flex gap-6 min-h-0">
        <Card title="Recovered Segments" className="flex-1">
          <div className="overflow-auto h-full -mx-6 px-6">
            <table className="w-full text-left text-sm">
              <thead className="sticky top-0 bg-surface z-10 text-muted border-b border-border">
                <tr>
                  <th className="pb-3 font-medium">CH</th>
                  <th className="pb-3 font-medium">Time (Norm)</th>
                  <th className="pb-3 font-medium">Offset</th>
                  <th className="pb-3 font-medium">Source</th>
                  <th className="pb-3 font-medium text-right">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {segments.map(seg => (
                  <tr 
                    key={seg.id} 
                    onClick={() => setSelectedSeg(seg)}
                    className={`cursor-pointer transition-colors ${selectedSeg?.id === seg.id ? 'bg-indigo/20' : 'hover:bg-white/5'}`}
                  >
                    <td className="py-3 px-2 font-mono">{seg.channel}</td>
                    <td className="py-3 px-2">{seg.normalized_time || seg.dvr_time}</td>
                    <td className="py-3 px-2 font-mono text-xs">0x{seg.offset.toString(16).toUpperCase()}</td>
                    <td className="py-3 px-2">
                      <span className={`px-2 py-1 rounded text-xs ${seg.source === 'indexed' ? 'bg-accent/20 text-accent' : 'bg-success/20 text-success'}`}>
                        {seg.source}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-right">
                      <div className="w-16 h-1.5 bg-black/50 rounded ml-auto overflow-hidden">
                        <div className="h-full bg-success" style={{ width: `${seg.confidence * 100}%` }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {segments.length === 0 && <div className="text-center text-muted mt-8">No segments recovered</div>}
          </div>
        </Card>

        <Card title="Preview" className="w-96 flex flex-col shrink-0">
          {selectedSeg ? (
            <div className="flex flex-col h-full">
              <div className="aspect-video bg-black rounded-lg overflow-hidden border border-border flex items-center justify-center relative mb-4">
                {selectedSeg.file_hash ? (
                  <video 
                    src={`http://localhost:8000/api/clip/${selectedSeg.id}`} 
                    controls 
                    autoPlay 
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="text-muted flex flex-col items-center">
                    <PlayCircle className="w-12 h-12 mb-2 opacity-50" />
                    <span>Video not available</span>
                  </div>
                )}
              </div>
              <div className="bg-black/20 p-4 rounded-lg border border-white/5 space-y-3 flex-1">
                <div>
                  <p className="text-xs text-muted mb-1">SHA-256 Hash</p>
                  <p className="font-mono text-xs break-all text-accent">{selectedSeg.file_hash || 'N/A'}</p>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <p className="text-xs text-muted mb-1">DVR Time</p>
                    <p className="text-sm">{selectedSeg.dvr_time}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted mb-1">Norm Time</p>
                    <p className="text-sm text-success font-medium">{selectedSeg.normalized_time || '-'}</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted">
              Select a segment to preview
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
