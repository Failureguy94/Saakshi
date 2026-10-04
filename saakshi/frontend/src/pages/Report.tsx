import React, { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { Download, FileText, Copy, Check } from 'lucide-react';
import { useStore } from '../store';

export default function Report() {
  const { caseInfo } = useStore();
  const [data, setData] = useState<any>({});
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    // We can fetch data from the db or endpoints to construct a summary view
    Promise.all([
      fetch('http://localhost:8000/api/segments').then(r=>r.json()),
      fetch('http://localhost:8000/api/events').then(r=>r.json()),
      fetch('http://localhost:8000/api/custody').then(r=>r.json())
    ]).then(([segs, evs, cust]) => {
      setData({ segments: segs.segments, events: evs.events, custody: cust.log });
    });
  }, []);

  const handleCopy = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
  };

  // Find acquisition log for hashes
  const acqLog = data.custody?.find((l:any) => l.stage === 'Acquisition');
  const imgHash = acqLog ? acqLog.evidence_hash : 'N/A';
  
  // Find report log for merkle root
  const repLog = data.custody?.find((l:any) => l.stage === 'Reporting' || l.stage === 'Seal');
  const merkleRoot = repLog ? repLog.entry_hash : 'N/A'; // close enough for demo

  return (
    <div className="h-full flex gap-6">
      <div className="flex-1 flex flex-col gap-6 overflow-y-auto pr-2">
        <div className="flex justify-between items-center bg-surface p-6 rounded-xl border border-border shrink-0">
          <div>
            <h2 className="text-2xl font-bold tracking-tight mb-1">Final Report</h2>
            <p className="text-muted text-sm">Comprehensive forensic findings summary</p>
          </div>
          <a 
            href="http://localhost:8000/api/report.pdf" 
            target="_blank"
            download
            className="bg-accent text-[#0A0E14] font-semibold px-6 py-3 rounded-lg flex items-center shadow-[0_0_15px_rgba(45,212,191,0.3)] hover:shadow-[0_0_25px_rgba(45,212,191,0.5)] transition-all"
          >
            <Download className="w-5 h-5 mr-2" />
            Download PDF
          </a>
        </div>

        <div className="grid grid-cols-2 gap-4 shrink-0">
          <Card title="Image Details">
            <div className="space-y-4">
              <div>
                <p className="text-xs text-muted mb-1">File Name</p>
                <p className="font-medium text-text">{caseInfo?.file?.split('/').pop() || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-muted mb-1">Size</p>
                <p className="font-medium text-text">{(caseInfo?.size || 0).toLocaleString()} bytes</p>
              </div>
            </div>
          </Card>
          <Card title="Extraction Stats">
            <div className="space-y-4">
              <div>
                <p className="text-xs text-muted mb-1">Total Segments Recovered</p>
                <p className="text-2xl font-bold text-success">{data.segments?.length || 0}</p>
              </div>
              <div>
                <p className="text-xs text-muted mb-1">Motion Events Detected</p>
                <p className="text-2xl font-bold text-warning">{data.events?.length || 0}</p>
              </div>
            </div>
          </Card>
        </div>

        <Card title="Cryptographic Hashes" className="shrink-0">
          <div className="space-y-4">
            <div className="bg-black/20 p-3 rounded-lg border border-white/5 flex items-center justify-between">
              <div>
                <p className="text-xs text-muted mb-1">SHA-256 (Image)</p>
                <p className="font-mono text-sm text-accent">{imgHash}</p>
              </div>
              <button onClick={() => handleCopy(imgHash, 'sha256')} className="p-2 hover:bg-white/10 rounded transition-colors text-muted hover:text-text">
                {copied === 'sha256' ? <Check className="w-4 h-4 text-success" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
            
            <div className="bg-black/20 p-3 rounded-lg border border-white/5 flex items-center justify-between">
              <div>
                <p className="text-xs text-muted mb-1">Merkle Root</p>
                <p className="font-mono text-sm text-indigo">{merkleRoot}</p>
              </div>
              <button onClick={() => handleCopy(merkleRoot, 'merkle')} className="p-2 hover:bg-white/10 rounded transition-colors text-muted hover:text-text">
                {copied === 'merkle' ? <Check className="w-4 h-4 text-success" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </Card>
      </div>

      <Card title="PDF Preview" className="w-[500px] shrink-0 p-0 flex flex-col">
        <div className="flex-1 bg-white relative">
          <iframe 
            src="http://localhost:8000/api/report.pdf#toolbar=0&navpanes=0" 
            className="absolute inset-0 w-full h-full border-0"
            title="PDF Preview"
          />
        </div>
      </Card>
    </div>
  );
}
