import { create } from 'zustand';
import { CaseRecord } from '../api/client';

interface CaseState {
  activeCase: CaseRecord | null;
  setActiveCase: (c: CaseRecord | null) => void;
}

export const useCaseStore = create<CaseState>((set) => ({
  activeCase: null,
  setActiveCase: (activeCase) => set({ activeCase }),
}));
