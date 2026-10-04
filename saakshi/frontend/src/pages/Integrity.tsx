import React, { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { ShieldAlert, ShieldCheck, Link2, AlertTriangle, RefreshCcw } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Integrity() {
  const [log, setLog] = useState<any[]>([]);
  const [segments, setSegments] = useState<any[]>([]);
  const [verifyResult, setVerifyResult] = useState<any>(null);
  const [proof, setProof] = useState<any>(null);
  const [selectedClip, setSelectedClip] = useState<number | null>(null);

  const fetchLog = () => fetch('http://localhost:8000/api/custody').then(r=>r.json()).then(d=>setLog(d.log || []));
  const fetchSeg = () => fetch('http://localhost:8000/api/segments').then(r=>r.json()).then(d=>setSegments(d.segments || []));

  useEffect(() => {
    fetchLog();
    fetchSeg();
  }, []);

  const verifyChain = async () => {
    const res = await fetch('http://localhost:8000/api/custody/verify', { method: 'POST' });
    const data = await res.json();
    setVerifyResult(data);
  };

  const getProof = async (clipId: number) => {
    setSelectedClip(clipId);
    const res = await fetch(`http://localhost:8000/api/merkle/proof/${clipId}`);
    const data = await res.json();
    setProof(data);
  };

  const tamper = async () => {
    if (!selectedClip) return alert("Select a clip for proof first");
    await fetch('http://localhost:8000/api/custody/tamper', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ clip_id: selectedClip })
    });
    await verifyChain(); // re-verify to show failure
  };

  const restore = async () => {
    if (!selectedClip) return;
    await fetch('http://localhost:8000/api/custody/restore', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ clip_id: selectedClip })
    });
    await verifyChain();
  };

  return (
    <div className="h-full flex flex-col gap-6">
      <div className="flex justify-between items-center bg-surface p-6 rounded-xl border border-border shrink-0">
        <div>
          <h2 className="text-2xl font-bold tracking-tight mb-1 flex items-center">
            Integrity Check
            {verifyResult && (
              verifyResult.chain_valid && verifyResult.manifest_valid ? 
                <ShieldCheck className="w-6 h-6 ml-3 text-success" /> : 
                <ShieldAlert className="w-6 h-6 ml-3 text-danger" />
            )}
          </h2>
          <p className="text-muted text-sm">Cryptographic verification of evidence custody</p>
        </div>
        <button 
          onClick={verifyChain}
          className="bg-indigo text-white font-semibold px-6 py-3 rounded-lg flex items-center shadow-[0_0_15px_rgba(99,102,241,0.3)] hover:shadow-[0_0_25px_rgba(99,102,241,0.5)] transition-all"
        >
          <ShieldCheck className="w-5 h-5 mr-2" />
          Verify Chain & Manifest
        </button>
      </div>

      {verifyResult && (!verifyResult.chain_valid || !verifyResult.manifest_valid) && (
        <Card className="shrink-0 border-danger bg-danger/10">
          <div className="flex items-start space-x-4 text-danger">
            <AlertTriangle className="w-6 h-6 mt-1" />
            <div>
              <h3 className="font-bold text-lg mb-2">Integrity Violation Detected</h3>
              {!verifyResult.chain_valid && <p>Custody chain broken at entry ID {verifyResult.failed_chain_id}</p>}
              {!verifyResult.manifest_valid && (
                <div className="mt-2 font-mono text-sm space-y-1">
                  <p><strong>File:</strong> {verifyResult.failed_path}</p>
                  <p><strong>Expected:</strong> {verifyResult.expected_hash}</p>
                  <p><strong>Actual:</strong> {verifyResult.actual_hash}</p>
                </div>
              )}
              {!verifyResult.manifest_valid && (
                <button onClick={restore} className="mt-4 flex items-center px-4 py-2 bg-danger text-white rounded font-medium hover:bg-danger/80">
                  <RefreshCcw className="w-4 h-4 mr-2" />
                  Restore Backup
                </button>
              )}
            </div>
          </div>
        </Card>
      )}

      <div className="flex-1 flex gap-6 min-h-0">
        <Card title="Chain of Custody" className="flex-1">
          <div className="overflow-y-auto pr-4 space-y-4">
            {log.length === 0 && <p className="text-muted text-center py-4">No log entries</p>}
            {log.map((entry, i) => (
              <div key={entry.id} className="relative pl-8">
                {i !== log.length - 1 && <div className="absolute top-8 bottom-0 left-[11px] w-0.5 bg-border -mb-4" />}
                <div className="absolute top-2 left-0 w-6 h-6 bg-surface border-2 border-indigo rounded-full z-10 flex items-center justify-center">
                  <Link2 className="w-3 h-3 text-indigo" />
                </div>
                <div className="bg-black/20 border border-white/5 p-4 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-bold text-text">{entry.stage}</span>
                    <span className="text-xs text-muted font-mono">{entry.timestamp}</span>
                  </div>
                  <p className="text-sm text-muted mb-3">{entry.description}</p>
                  <div className="space-y-1">
                    <div className="flex text-xs font-mono">
                      <span className="w-16 text-muted">Hash:</span>
                      <span className="text-accent truncate" title={entry.entry_hash}>{entry.entry_hash.substring(0, 32)}...</span>
                    </div>
                    {i > 0 && (
                      <div className="flex text-xs font-mono">
                        <span className="w-16 text-muted">Prev:</span>
                        <span className="text-indigo truncate" title={entry.prev_hash}>{entry.prev_hash.substring(0, 32)}...</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Merkle Proof & Tamper Test" className="w-[450px] shrink-0 flex flex-col">
          <div className="mb-4">
            <label className="block text-sm font-medium text-muted mb-2">Select Clip to Prove</label>
            <select 
              className="w-full bg-black/20 border border-border rounded-lg p-2 text-sm text-text"
              onChange={(e) => getProof(Number(e.target.value))}
              value={selectedClip || ''}
            >
              <option value="" disabled>-- Select --</option>
              {segments.map(s => <option key={s.id} value={s.id}>Segment {s.id} (CH {s.channel})</option>)}
            </select>
          </div>
          
          <div className="flex-1 bg-black/20 border border-white/5 rounded-lg p-4 overflow-y-auto mb-4 font-mono text-xs space-y-2">
            {proof ? (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <p className="text-accent mb-2">Target Hash: <br/><span className="text-white opacity-80">{proof.hash}</span></p>
                <div className="text-muted">Proof Path:</div>
                {proof.proof?.map((p: any, i: number) => (
                  <div key={i} className="pl-4 py-1 border-l-2 border-border mt-1">
                    <span className="text-indigo">{p.direction === 'left' ? 'L' : 'R'}</span> : <span className="opacity-70">{p.hash.substring(0, 40)}...</span>
                  </div>
                ))}
              </motion.div>
            ) : (
              <div className="text-muted text-center h-full flex items-center justify-center">Select a clip to generate proof</div>
            )}
          </div>
          
          <button 
            onClick={tamper}
            disabled={!selectedClip}
            className="w-full bg-danger/20 text-danger border border-danger/50 hover:bg-danger/30 font-semibold px-4 py-3 rounded-lg flex justify-center items-center transition-colors disabled:opacity-50"
          >
            <AlertTriangle className="w-5 h-5 mr-2" />
            Run Tamper Test
          </button>
        </Card>
      </div>
    </div>
  );
}
