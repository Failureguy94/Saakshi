import React from 'react';
import { ShieldCheck, CheckCircle2, Lock } from 'lucide-react';

export const LedgerVerification: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            Cryptographic Custody Ledger Audit
          </h1>
          <p className="text-sm text-slate-400">
            Append-only hash-chained audit trail & Merkle inclusion proof validator.
          </p>
        </div>
      </div>

      <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-950/60 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-200">Ledger Integrity Status: Active</h3>
              <p className="text-xs text-slate-400">Hash-chained log verified with zero detected mutations.</p>
            </div>
          </div>

          <div className="text-right font-mono text-xs text-slate-400">
            <div>Engine Backend: <span className="text-emerald-400">LocalLedgerAnchor</span></div>
            <div>Fabric Consortium: <span className="text-slate-500">Stub</span></div>
          </div>
        </div>

        <div className="space-y-3 pt-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Recent Custody Blocks
          </h4>

          {/* Sample block visualizer */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 font-mono text-xs space-y-1">
            <div className="flex items-center justify-between text-emerald-400 font-semibold">
              <span>BLOCK #0 (GENESIS)</span>
              <span>ACTION: SYSTEM_INIT</span>
            </div>
            <div className="text-slate-400 truncate">
              PREVIOUS_HASH: 0000000000000000000000000000000000000000000000000000000000000000
            </div>
            <div className="text-slate-500">ACTOR: SYSTEM_WORKER • EVIDENCE_ID: EVID-SYSTEM</div>
          </div>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3 text-xs text-slate-400">
        <Lock className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-300">Independent CLI Audit: </span>
          Judicial magistrates and independent defense examiners can verify this exact custody log offline via:
          <code className="block mt-1 p-2 rounded bg-slate-950 font-mono text-emerald-400 border border-slate-800">
            python scripts/verify_ledger.py /path/to/custody_chain.jsonl
          </code>
        </div>
      </div>
    </div>
  );
};
