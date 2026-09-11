"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Report, ReportType } from "@/types/report";
import type { ComplianceReport } from "@/types/compliance";

export type ReportsTab =
  | "templates"
  | "history"
  | "compliance"
  | "audit";

interface ReportState {
  reports: Report[];
  complianceReports: ComplianceReport[];
  selectedReport: Report | null;
  selectedTemplate: ReportType | null;
  previewOpen: boolean;
  generateDialogOpen: boolean;
  activeTab: ReportsTab;
  searchQuery: string;
  filterCaseId: string;

  setReports: (reports: Report[]) => void;
  setComplianceReports: (reports: ComplianceReport[]) => void;
  setSelectedReport: (report: Report | null) => void;
  setSelectedTemplate: (template: ReportType | null) => void;
  setPreviewOpen: (open: boolean) => void;
  setGenerateDialogOpen: (open: boolean) => void;
  setActiveTab: (tab: ReportsTab) => void;
  setSearchQuery: (query: string) => void;
  setFilterCaseId: (caseId: string) => void;
}

export const useReportStore = create<ReportState>()(
  persist(
    (set) => ({
      reports: [],
      complianceReports: [],
      selectedReport: null,
      selectedTemplate: null,
      previewOpen: false,
      generateDialogOpen: false,
      activeTab: "templates",
      searchQuery: "",
      filterCaseId: "",

      setReports: (reports) => set({ reports }),
      setComplianceReports: (reports) => set({ complianceReports: reports }),
      setSelectedReport: (report) =>
        set({ selectedReport: report, previewOpen: !!report }),
      setSelectedTemplate: (template) => set({ selectedTemplate: template }),
      setPreviewOpen: (open) =>
        set((state) => ({
          previewOpen: open,
          selectedReport: open ? state.selectedReport : null,
        })),
      setGenerateDialogOpen: (open) => set({ generateDialogOpen: open }),
      setActiveTab: (tab) => set({ activeTab: tab }),
      setSearchQuery: (query) => set({ searchQuery: query }),
      setFilterCaseId: (caseId) => set({ filterCaseId: caseId }),
    }),
    {
      name: "crimekit-reports-store",
      partialize: (state) => ({
        activeTab: state.activeTab,
      }),
    },
  ),
);
