import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { CaseView } from './pages/CaseView';
import { EvidenceTree } from './pages/EvidenceTree';
import { DiskMap } from './pages/DiskMap';
import { MultiCameraTimeline } from './pages/MultiCameraTimeline';
import { LedgerVerification } from './pages/LedgerVerification';
import { Reports } from './pages/Reports';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="flex flex-col h-screen overflow-hidden bg-slate-950 text-slate-100">
          <Navbar />
          <div className="flex flex-1 overflow-hidden">
            <Sidebar />
            <main className="flex-1 overflow-y-auto p-6 bg-slate-950">
              <div className="max-w-7xl mx-auto">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/cases" element={<CaseView />} />
                  <Route path="/evidence" element={<EvidenceTree />} />
                  <Route path="/disk-map" element={<DiskMap />} />
                  <Route path="/timeline" element={<MultiCameraTimeline />} />
                  <Route path="/ledger" element={<LedgerVerification />} />
                  <Route path="/reports" element={<Reports />} />
                </Routes>
              </div>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
};
