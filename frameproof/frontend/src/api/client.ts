/**
 * FrameProof Typed Frontend API Client
 */

export interface SystemHealth {
  status: string;
  app: string;
  version: string;
  offline_mode: boolean;
}

export interface CaseRecord {
  id: string;
  case_number: string;
  title: string;
  description: string | null;
  investigator_name: string;
  agency: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CreateCasePayload {
  case_number: string;
  title: string;
  description?: string;
  investigator_name: string;
  agency?: string;
}

const API_BASE = '/api';

export async function fetchHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new Error(`Failed to fetch health status: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchCases(): Promise<CaseRecord[]> {
  const res = await fetch(`${API_BASE}/cases`);
  if (!res.ok) {
    throw new Error(`Failed to fetch cases: ${res.statusText}`);
  }
  return res.json();
}

export async function createCase(payload: CreateCasePayload): Promise<CaseRecord> {
  const res = await fetch(`${API_BASE}/cases`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create case: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchCase(caseId: string): Promise<CaseRecord> {
  const res = await fetch(`${API_BASE}/cases/${caseId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch case ${caseId}: ${res.statusText}`);
  }
  return res.json();
}
