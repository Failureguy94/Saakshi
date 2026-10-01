import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchCases, createCase, CreateCasePayload } from '../api/client';
import { FolderGit2, Plus, ShieldCheck } from 'lucide-react';
import { useCaseStore } from '../store/caseStore';

export const CaseView: React.FC = () => {
  const queryClient = useQueryClient();
  const setActiveCase = useCaseStore((state) => state.setActiveCase);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<CreateCasePayload>({
    case_number: '',
    title: '',
    description: '',
    investigator_name: '',
    agency: 'State Forensic Science Laboratory',
  });

  const { data: cases, isLoading } = useQuery({
    queryKey: ['cases'],
    queryFn: fetchCases,
  });

  const createMutation = useMutation({
    mutationFn: createCase,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      setActiveCase(data);
      setShowModal(false);
      setForm({
        case_number: '',
        title: '',
        description: '',
        investigator_name: '',
        agency: 'State Forensic Science Laboratory',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.case_number || !form.title || !form.investigator_name) return;
    createMutation.mutate(form);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FolderGit2 className="w-5 h-5 text-emerald-400" />
            Case Management
          </h1>
          <p className="text-sm text-slate-400">Initialize and manage forensic DVR seizure case files.</p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Forensic Case
        </button>
      </div>

      {isLoading ? (
        <div className="text-sm text-slate-500">Loading cases...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cases?.map((c) => (
            <div
              key={c.id}
              className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors space-y-3 cursor-pointer"
              onClick={() => setActiveCase(c)}
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-mono text-xs text-emerald-400 font-semibold">{c.case_number}</span>
                  <h3 className="font-semibold text-slate-200 mt-1">{c.title}</h3>
                </div>
                <ShieldCheck className="w-4 h-4 text-slate-500" />
              </div>
              <p className="text-xs text-slate-400 line-clamp-2">{c.description || 'No description provided.'}</p>
              <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
                <span>{c.investigator_name}</span>
                <span>{new Date(c.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-bold text-white">Register Forensic Case</h2>

            {createMutation.isError && (
              <div className="p-3 rounded-lg bg-red-950/60 border border-red-500/40 text-red-300 text-xs">
                {(createMutation.error as Error).message}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Official Case / FIR Number *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. FIR-892/2026"
                  value={form.case_number}
                  onChange={(e) => setForm({ ...form, case_number: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Case Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Bank Robbery DVR Seizure"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Investigator Name / Badge *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Insp. S. Sharma"
                  value={form.investigator_name}
                  onChange={(e) => setForm({ ...form, investigator_name: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Forensic Agency</label>
                <input
                  type="text"
                  value={form.agency}
                  onChange={(e) => setForm({ ...form, agency: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description / Notes</label>
                <textarea
                  rows={3}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold disabled:opacity-50"
                >
                  {createMutation.isPending ? 'Registering...' : 'Register Case'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
