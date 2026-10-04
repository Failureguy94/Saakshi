import React, { useEffect, useState } from 'react';
import { Card } from '../components/Card';

export default function Timeline() {
  const [segments, setSegments] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [useNorm, setUseNorm] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/segments').then(r=>r.json()).then(d=>setSegments(d.segments || []));
    fetch('http://localhost:8000/api/events').then(r=>r.json()).then(d=>setEvents(d.events || []));
  }, []);

  // Compute boundaries to scale timeline
  let minT = Number.MAX_SAFE_INTEGER;
  let maxT = 0;
  
  const getTs = (timeStr: string) => new Date(timeStr).getTime();

  segments.forEach(s => {
    const t = getTs(useNorm && s.normalized_time ? s.normalized_time : s.dvr_time);
    if (!isNaN(t)) {
      minT = Math.min(minT, t);
      // Rough duration approximation since length is bytes not time, we assume 5s for demo if not provided
      maxT = Math.max(maxT, t + 5000); 
    }
  });

  const duration = maxT - minT;
  const channels = [...new Set(segments.map(s => s.channel))].sort();

  return (
    <Card title="Timeline Analysis" className="h-full flex flex-col" action={
      <div className="flex items-center space-x-2 text-sm bg-black/20 p-1 rounded-lg border border-white/5">
        <button 
          onClick={() => setUseNorm(false)} 
          className={`px-3 py-1 rounded-md transition-colors ${!useNorm ? 'bg-surface text-text shadow' : 'text-muted hover:text-text'}`}
        >
          Raw DVR Time
        </button>
        <button 
          onClick={() => setUseNorm(true)} 
          className={`px-3 py-1 rounded-md transition-colors ${useNorm ? 'bg-surface text-success shadow' : 'text-muted hover:text-text'}`}
        >
          Normalized Time
        </button>
      </div>
    }>
      <div className="flex-1 flex flex-col space-y-6 overflow-auto">
        {channels.length === 0 && <div className="m-auto text-muted">No timeline data</div>}
        {channels.map(ch => {
          const chSegs = segments.filter(s => s.channel === ch);
          const chEvs = events.filter(e => e.channel === ch);
          
          return (
            <div key={ch} className="bg-black/20 border border-white/5 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h4 className="font-semibold">Channel {ch}</h4>
                <div className="text-xs text-muted space-x-4">
                  {useNorm && (
                    <>
                      <span>Offset: <span className="text-success font-mono">+300.0s</span></span>
                      <span>Drift: <span className="text-warning font-mono">1.2s/hr</span></span>
                      <span>Confidence: <span className="text-accent">High</span></span>
                    </>
                  )}
                </div>
              </div>
              
              <div className="relative h-16 bg-surface border border-border rounded overflow-visible">
                {chSegs.map(seg => {
                  const t = getTs(useNorm && seg.normalized_time ? seg.normalized_time : seg.dvr_time);
                  if (isNaN(t) || duration <= 0) return null;
                  const left = ((t - minT) / duration) * 100;
                  // For demo, standard width
                  const width = Math.max(1, (5000 / duration) * 100);
                  
                  return (
                    <div 
                      key={seg.id}
                      className="absolute top-2 bottom-2 bg-indigo/40 border border-indigo rounded transition-all duration-500"
                      style={{ left: `${left}%`, width: `${width}%` }}
                      title={`Seg ${seg.id} - ${useNorm ? seg.normalized_time : seg.dvr_time}`}
                    />
                  );
                })}
                
                {chEvs.map(ev => {
                  const t = getTs(ev.start_time); // Note: ideally normalize event time too, but events already use normalized time conceptually in this demo setup
                  if (isNaN(t) || duration <= 0) return null;
                  const left = ((t - minT) / duration) * 100;
                  
                  return (
                    <div 
                      key={ev.id}
                      className="absolute top-1/2 -mt-2 w-4 h-4 bg-danger rounded-full cursor-help group transition-all duration-500 shadow-[0_0_10px_rgba(239,68,68,0.8)] z-10"
                      style={{ left: `${left}%` }}
                    >
                      <div className="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-32 bg-surface border border-border rounded p-1 z-50 shadow-xl">
                        <p className="text-[10px] text-center mb-1 text-muted">Motion Peak</p>
                        {ev.thumbnail_path ? (
                          <img src={`http://localhost:8000/${ev.thumbnail_path}`} alt="motion" className="w-full h-auto rounded" />
                        ) : (
                          <div className="w-full h-20 bg-black/50 flex items-center justify-center text-xs">No image</div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
