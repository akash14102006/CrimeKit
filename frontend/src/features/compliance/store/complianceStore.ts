"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { LegalHold, RetentionPolicy, ComplianceReport } from "@/types/compliance";

export type ComplianceTab =
  | "dashboard"
  | "gdpr"
  | "legal-hold"
  | "retention"
  | "timeline"
  | "audit"
  | "export";

interface ComplianceState {
  legalHolds: LegalHold[];
  retentionPolicies: RetentionPolicy[];
  complianceReports: ComplianceReport[];
  selectedHold: LegalHold | null;
  selectedPolicy: RetentionPolicy | null;
  activeTab: ComplianceTab;
  searchQuery: string;

  setLegalHolds: (holds: LegalHold[]) => void;
  setRetentionPolicies: (policies: RetentionPolicy[]) => void;
  setComplianceReports: (reports: ComplianceReport[]) => void;
  setSelectedHold: (hold: LegalHold | null) => void;
  setSelectedPolicy: (policy: RetentionPolicy | null) => void;
  setActiveTab: (tab: ComplianceTab) => void;
  setSearchQuery: (query: string) => void;
}

export const useComplianceStore = create<ComplianceState>()(
  persist(
    (set) => ({
      legalHolds: [],
      retentionPolicies: [],
      complianceReports: [],
      selectedHold: null,
      selectedPolicy: null,
      activeTab: "dashboard",
      searchQuery: "",

      setLegalHolds: (holds) => set({ legalHolds: holds }),
      setRetentionPolicies: (policies) => set({ retentionPolicies: policies }),
      setComplianceReports: (reports) => set({ complianceReports: reports }),
      setSelectedHold: (hold) => set({ selectedHold: hold }),
      setSelectedPolicy: (policy) => set({ selectedPolicy: policy }),
      setActiveTab: (tab) => set({ activeTab: tab }),
      setSearchQuery: (query) => set({ searchQuery: query }),
    }),
    {
      name: "crimekit-compliance-store",
      partialize: (state) => ({
        activeTab: state.activeTab,
      }),
    },
  ),
);
