import React, { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { Lock, File as FileIcon, Search } from 'lucide-react';
import { useStore } from '../store';
import { motion } from 'framer-motion';

interface HexRow {
  offset: string;
  hex: string;
  ascii: string;
}

export default function Evidence() {
  const { caseInfo } = useStore();
  const [hexData, setHexData] = useState<HexRow[]>([]);
  const [matchInfo, setMatchInfo] = useState<{ match: string; confidence: number } | null>(null);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/evidence/hex?offset=0&length=256')
      .then(r => r.json())
      .then(d => setHexData(d.data || []));
      
    // Ideally this comes from the state or db, but for demo just calling it if case exists
    if (caseInfo && caseInfo.size > 0) {
      fetch('http://localhost:8000/api/stage/1', { method: 'POST' })
        .then(r => r.json())
        .then(d => setMatchInfo(d));
    }
  }, [caseInfo]);

  return (
    <div className="h-full flex flex-col gap-6">
      <div className="grid grid-cols-3 gap-6 shrink-0">
        <Card className="col-span-2">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-3">
              <FileIcon className="w-8 h-8 text-indigo" />
              <div>
                <h3 className="font-semibold text-lg">{caseInfo?.file?.split('/').pop() || 'No Evidence'}</h3>
                <p className="text-sm text-muted">Raw bit-stream image</p>
              </div>
            </div>
            <div className="flex items-center px-3 py-1 bg-warning/10 text-warning rounded-full border border-warning/20">
              <Lock className="w-4 h-4 mr-2" />
              <span className="text-sm font-medium">Read Only</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 mt-6 p-4 bg-black/20 rounded-lg border border-white/5">
            <div>
              <p className="text-xs text-muted mb-1">Path</p>
              <p className="font-mono text-sm">{caseInfo?.file || '-'}</p>
            </div>
            <div>
              <p className="text-xs text-muted mb-1">Size</p>
              <p className="font-mono text-sm">{(caseInfo?.size || 0).toLocaleString()} bytes</p>
            </div>
          </div>
        </Card>

        <Card title="Identification" className="items-center justify-center text-center">
          {matchInfo ? (
            <div className="flex flex-col items-center">
              <div className="relative w-32 h-32 flex items-center justify-center mb-4">
                <svg className="absolute inset-0 w-full h-full transform -rotate-90">
                  <circle cx="64" cy="64" r="60" className="stroke-black/50" strokeWidth="8" fill="none" />
                  <motion.circle 
                    cx="64" cy="64" r="60" 
                    className="stroke-success" 
                    strokeWidth="8" fill="none" 
                    strokeDasharray="377" 
                    initial={{ strokeDashoffset: 377 }}
                    animate={{ strokeDashoffset: 377 - (377 * matchInfo.confidence) }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                  />
                </svg>
                <div className="text-2xl font-bold">{Math.round(matchInfo.confidence * 100)}%</div>
              </div>
              <p className="text-lg font-medium text-text">{matchInfo.match}</p>
              <p className="text-sm text-muted">Signature Confidence</p>
            </div>
          ) : (
            <div className="text-muted flex flex-col items-center">
              <Search className="w-8 h-8 mb-2 opacity-50" />
              <p>No identification data</p>
            </div>
          )}
        </Card>
      </div>

      <Card title="Hex Viewer" className="flex-1">
        <div className="font-mono text-sm whitespace-pre">
          <div className="flex text-muted mb-2 border-b border-border pb-2">
            <span className="w-24">Offset</span>
            <span className="flex-1 text-center">Hexadecimal</span>
            <span className="w-48 text-right pr-4">ASCII</span>
          </div>
          {hexData.map((row, i) => (
            <div key={i} className="flex hover:bg-white/5 py-1 px-2 rounded -mx-2 transition-colors">
              <span className="w-24 text-indigo/70">{row.offset}</span>
              <span className="flex-1 text-center tracking-widest text-[#E6EDF7]">
                {/* Highlight SEGH if present (dumb search for 53 45 47 48) */}
                {row.hex.split(' ').map((h, j) => {
                  const isSig = (h==='53' || h==='45' || h==='47' || h==='48'); // naive
                  return (
                    <span key={j} className={isSig ? "text-accent font-bold" : ""}>
                      {h}{" "}
                    </span>
                  );
                })}
              </span>
              <span className="w-48 text-right pr-4 text-muted tracking-[0.2em]">{row.ascii}</span>
            </div>
          ))}
          {hexData.length === 0 && <div className="text-center text-muted py-8">No data available</div>}
        </div>
      </Card>
    </div>
  );
}
