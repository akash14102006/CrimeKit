import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { WorkspaceEvidenceItem } from "@/types/workspace";

export type WorkspacePanel = "evidence" | "timeline" | "graph" | "ai" | "custody" | "processing" | "risks";

interface WorkspaceState {
  caseId: string | null;
  selectedEvidenceId: string | null;
  selectedEvidence: WorkspaceEvidenceItem | null;
  evidenceSearch: string;
  evidenceFilter: string;
  timelineFilter: string;
  activeBottomTab: "timeline" | "custody" | "activity";
  rightPanelTab: "ai" | "processing" | "risks";
  leftPanelCollapsed: boolean;
  bottomPanelCollapsed: boolean;
  rightPanelCollapsed: boolean;
  pinnedEvidenceIds: string[];
  recentEvidenceIds: string[];
}

interface WorkspaceActions {
  setCaseId: (caseId: string) => void;
  selectEvidence: (evidence: WorkspaceEvidenceItem | null) => void;
  setSelectedEvidenceId: (id: string | null) => void;
  setSearch: (search: string) => void;
  setEvidenceSearch: (search: string) => void;
  setEvidenceFilter: (filter: string) => void;
  setTimelineFilter: (filter: string) => void;
  setActiveBottomTab: (tab: "timeline" | "custody" | "activity") => void;
  setRightPanelTab: (tab: "ai" | "processing" | "risks") => void;
  toggleLeftPanel: () => void;
  toggleBottomPanel: () => void;
  toggleRightPanel: () => void;
  pinEvidence: (id: string) => void;
  unpinEvidence: (id: string) => void;
  addRecentEvidence: (id: string) => void;
  reset: () => void;
}

const initialState: WorkspaceState = {
  caseId: null,
  selectedEvidenceId: null,
  selectedEvidence: null,
  evidenceSearch: "",
  evidenceFilter: "all",
  timelineFilter: "all",
  activeBottomTab: "timeline",
  rightPanelTab: "ai",
  leftPanelCollapsed: false,
  bottomPanelCollapsed: false,
  rightPanelCollapsed: false,
  pinnedEvidenceIds: [],
  recentEvidenceIds: [],
};

export const useWorkspaceStore = create<WorkspaceState & WorkspaceActions>()(
  persist(
    (set) => ({
      ...initialState,

      setCaseId: (caseId) => set({ ...initialState, caseId }),

      selectEvidence: (evidence) =>
        set({
          selectedEvidence: evidence,
          selectedEvidenceId: evidence?.id ?? null,
        }),

      setSelectedEvidenceId: (id) =>
        set({ selectedEvidenceId: id }),

      setSearch: (evidenceSearch) => set({ evidenceSearch }),
      setEvidenceSearch: (evidenceSearch) => set({ evidenceSearch }),
      setEvidenceFilter: (evidenceFilter) => set({ evidenceFilter }),
      setTimelineFilter: (timelineFilter) => set({ timelineFilter }),
      setActiveBottomTab: (activeBottomTab) => set({ activeBottomTab }),
      setRightPanelTab: (rightPanelTab) => set({ rightPanelTab }),

      toggleLeftPanel: () =>
        set((state) => ({ leftPanelCollapsed: !state.leftPanelCollapsed })),
      toggleBottomPanel: () =>
        set((state) => ({ bottomPanelCollapsed: !state.bottomPanelCollapsed })),
      toggleRightPanel: () =>
        set((state) => ({ rightPanelCollapsed: !state.rightPanelCollapsed })),

      pinEvidence: (id) =>
        set((state) => ({
          pinnedEvidenceIds: [...new Set([...state.pinnedEvidenceIds, id])],
        })),
      unpinEvidence: (id) =>
        set((state) => ({
          pinnedEvidenceIds: state.pinnedEvidenceIds.filter((eid) => eid !== id),
        })),

      addRecentEvidence: (id) =>
        set((state) => ({
          recentEvidenceIds: [
            id,
            ...state.recentEvidenceIds.filter((eid) => eid !== id),
          ].slice(0, 10),
        })),

      reset: () => set(initialState),
    }),
    {
      name: "crimekit-workspace",
      partialize: (state) => ({
        leftPanelCollapsed: state.leftPanelCollapsed,
        bottomPanelCollapsed: state.bottomPanelCollapsed,
        rightPanelCollapsed: state.rightPanelCollapsed,
        pinnedEvidenceIds: state.pinnedEvidenceIds,
        activeBottomTab: state.activeBottomTab,
        rightPanelTab: state.rightPanelTab,
      }),
    },
  ),
);
