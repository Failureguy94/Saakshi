import React, { useEffect, useState, useRef } from 'react';
import { Play, CheckCircle2, Circle, Loader2, HardDrive } from 'lucide-react';
import { Card } from '../components/Card';
import { motion, AnimatePresence } from 'framer-motion';

const STAGES = [
  { id: 1, name: 'Identify', desc: 'Detect vendor signature' },
  { id: 2, name: 'Acquire', desc: 'Secure hash & snapshot' },
  { id: 3, name: 'Parse', desc: 'Read index tables' },
  { id: 4, name: 'Recover', desc: 'Carve video segments' },
  { id: 5, name: 'Analytics', desc: 'Timeline & Motion' },
  { id: 6, name: 'Seal', desc: 'Hash chain & Report' },
];

export default function Pipeline() {
  const [activeStage, setActiveStage] = useState<number>(0);
  const [completed, setCompleted] = useState<Set<number>>(new Set());
  const [logs, setLogs] = useState<string[]>([]);
  const [progress, setProgress] = useState<{ [stage: string]: number }>({});
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const es = new EventSource('http://localhost:8000/api/stream');
    es.addEventListener('log', (e) => {
      setLogs(prev => [...prev, e.data].slice(-100)); // keep last 100
    });
    es.addEventListener('progress', (e) => {
      try {
        const data = JSON.parse(e.data);
        setProgress(prev => ({ ...prev, [data.stage]: data.pct }));
      } catch (err) {}
    });
    return () => es.close();
  }, []);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const runStage = async (id: number) => {
    setActiveStage(id);
    try {
      const res = await fetch(`http://localhost:8000/api/stage/${id}`, { method: 'POST' });
      const data = await res.json();
      setLogs(prev => [...prev, `Result [${id}]: ${JSON.stringify(data)}`]);
      setCompleted(prev => new Set(prev).add(id));
    } catch (err) {
      setLogs(prev => [...prev, `Error [${id}]: ${err}`]);
    } finally {
      setActiveStage(0);
    }
  };

  const runAll = async () => {
    for (const stage of STAGES) {
      await runStage(stage.id);
    }
  };

  return (
    <div className="h-full flex gap-6">
      <div className="flex-1 flex flex-col gap-6">
        <div className="flex justify-between items-center bg-surface p-6 rounded-xl border border-border">
          <div>
            <h2 className="text-2xl font-bold tracking-tight mb-1">Analysis Pipeline</h2>
            <p className="text-muted text-sm">Automated extraction, recovery, and validation</p>
          </div>
          <button 
            onClick={runAll}
            disabled={activeStage !== 0}
            className="bg-accent text-[#0A0E14] font-semibold px-6 py-3 rounded-lg flex items-center shadow-[0_0_15px_rgba(45,212,191,0.3)] hover:shadow-[0_0_25px_rgba(45,212,191,0.5)] transition-all disabled:opacity-50"
          >
            <Play className="w-5 h-5 mr-2" fill="currentColor" />
            Run Full Analysis
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {STAGES.map((stage) => {
            const isRunning = activeStage === stage.id;
            const isDone = completed.has(stage.id);
            const pName = stage.id === 2 ? 'Acquire' : (stage.id === 4 ? 'Recover' : '');
            const stageProgress = pName ? (progress[pName] || 0) : (isRunning ? 50 : 0);
            
            return (
              <Card key={stage.id} className={`transition-all duration-300 ${isRunning ? 'ring-2 ring-indigo shadow-[0_0_20px_rgba(99,102,241,0.2)]' : ''}`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center space-x-3">
                    {isRunning ? (
                      <Loader2 className="w-6 h-6 text-indigo animate-spin" />
                    ) : isDone ? (
                      <CheckCircle2 className="w-6 h-6 text-success" />
                    ) : (
                      <Circle className="w-6 h-6 text-muted" />
                    )}
                    <h3 className="font-semibold text-lg">{stage.name}</h3>
                  </div>
                  <button 
                    onClick={() => runStage(stage.id)}
                    disabled={activeStage !== 0}
                    className="p-2 bg-white/5 hover:bg-white/10 rounded-md transition-colors disabled:opacity-50"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-sm text-muted mb-4 flex-1">{stage.desc}</p>
                
                <div className="h-1.5 bg-black/50 rounded-full overflow-hidden">
                  <motion.div 
                    className={`h-full ${isDone ? 'bg-success' : 'bg-indigo'}`}
                    initial={{ width: 0 }}
                    animate={{ width: isDone ? '100%' : (isRunning ? `${stageProgress}%` : '0%') }}
                    transition={{ duration: 0.2 }}
                  />
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Terminal Log */}
      <Card className="w-96 flex flex-col font-mono text-sm" title="Terminal Output">
        <div className="flex-1 overflow-y-auto space-y-2 text-muted">
          <AnimatePresence initial={false}>
            {logs.map((log, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, x: -10 }} 
                animate={{ opacity: 1, x: 0 }}
                className={`${log.includes('Error') ? 'text-danger' : log.includes('Result') ? 'text-success' : 'text-text'}`}
              >
                <span className="opacity-50 mr-2 text-xs">{(new Date()).toISOString().split('T')[1].slice(0,8)}</span>
                {log}
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={logsEndRef} />
        </div>
      </Card>
    </div>
  );
}
