import { create } from 'zustand';

interface SaakshiState {
  currentPage: string;
  setCurrentPage: (page: string) => void;
  caseInfo: { file: string; size: number; read_only: boolean } | null;
  setCaseInfo: (info: any) => void;
  stagesCompleted: number;
  setStagesCompleted: (n: number) => void;
}

export const useStore = create<SaakshiState>((set) => ({
  currentPage: 'Pipeline',
  setCurrentPage: (page) => set({ currentPage: page }),
  caseInfo: null,
  setCaseInfo: (info) => set({ caseInfo: info }),
  stagesCompleted: 0,
  setStagesCompleted: (n) => set({ stagesCompleted: n }),
}));
