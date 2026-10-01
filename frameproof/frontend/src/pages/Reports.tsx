import React from 'react';
import { FileCheck2, Download, Shield } from 'lucide-react';
import { useCaseStore } from '../store/caseStore';

export const Reports: React.FC = () => {
  const activeCase = useCaseStore((state) => state.activeCase);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FileCheck2 className="w-5 h-5 text-emerald-400" />
            Section 63 BSA Forensic Reports
          </h1>
          <p className="text-sm text-slate-400">
            Generate judicial forensic certificates complying with Section 63 of Bharatiya Sakshya Adhiniyam, 2023.
          </p>
        </div>

        <button
          disabled
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 text-slate-500 text-sm font-semibold cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          Export Court Dossier (Planned)
        </button>
      </div>

      <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="space-y-1">
            <h3 className="font-semibold text-slate-200">Statutory Certificate Preview</h3>
            <p className="text-xs text-slate-400">Admissibility affidavit for trial proceedings</p>
          </div>
          <Shield className="w-5 h-5 text-emerald-400" />
        </div>

        <div className="p-6 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 space-y-3 leading-relaxed">
          <div className="text-center font-bold text-slate-100 border-b border-slate-800 pb-2">
            CERTIFICATE UNDER SECTION 63 OF THE BHARATIYA SAKSHYA ADHINIYAM, 2023<br />
            <span className="text-slate-500 font-normal">(Section 65B of Indian Evidence Act, 1872)</span>
          </div>

          <p>
            Case Reference: <span className="text-emerald-400">{activeCase?.case_number || '[NO CASE SELECTED]'}</span><br />
            Investigating Officer: <span className="text-slate-200">{activeCase?.investigator_name || '[NAME PENDING]'}</span><br />
            Agency: <span className="text-slate-200">{activeCase?.agency || '[AGENCY PENDING]'}</span>
          </p>

          <p className="text-slate-400">
            I hereby certify that the digital video recordings and recovered video segments were extracted using FrameProof in a strictly air-gapped forensic environment. The cryptographic hash values and Merkle trees recorded herein verify that the original bit-stream copy remains uncorrupted and authentic.
          </p>
        </div>
      </div>
    </div>
  );
};
