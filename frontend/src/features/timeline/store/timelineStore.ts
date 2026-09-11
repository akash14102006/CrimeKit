import { create } from "zustand";
import { persist } from "zustand/middleware";

export type TimelineMode = "vertical" | "compact" | "grouped";
export type TimelineZoom = "minutes" | "hours" | "days" | "weeks" | "months";

interface TimelineState {
  mode: TimelineMode;
  zoom: TimelineZoom;
  searchQuery: string;
  sourceFilter: string;
  dateFrom: string;
  dateTo: string;
  selectedEventId: string | null;
  showCorrelation: boolean;
  caseId: string | null;
}

interface TimelineActions {
  setMode: (mode: TimelineMode) => void;
  setZoom: (zoom: TimelineZoom) => void;
  setSearchQuery: (query: string) => void;
  setSourceFilter: (filter: string) => void;
  setDateFrom: (date: string) => void;
  setDateTo: (date: string) => void;
  selectEvent: (id: string | null) => void;
  toggleCorrelation: () => void;
  setCaseId: (caseId: string | null) => void;
  reset: () => void;
}

const initialState: TimelineState = {
  mode: "vertical",
  zoom: "days",
  searchQuery: "",
  sourceFilter: "all",
  dateFrom: "",
  dateTo: "",
  selectedEventId: null,
  showCorrelation: false,
  caseId: null,
};

export const useTimelineStore = create<TimelineState & TimelineActions>()(
  persist(
    (set) => ({
      ...initialState,
      setMode: (mode) => set({ mode }),
      setZoom: (zoom) => set({ zoom }),
      setSearchQuery: (searchQuery) => set({ searchQuery }),
      setSourceFilter: (sourceFilter) => set({ sourceFilter }),
      setDateFrom: (dateFrom) => set({ dateFrom }),
      setDateTo: (dateTo) => set({ dateTo }),
      selectEvent: (selectedEventId) => set({ selectedEventId, showCorrelation: selectedEventId !== null }),
      toggleCorrelation: () => set((s) => ({ showCorrelation: !s.showCorrelation })),
      setCaseId: (caseId) => set({ caseId }),
      reset: () => set(initialState),
    }),
    {
      name: "crimekit-timeline",
      partialize: (state) => ({
        mode: state.mode,
        zoom: state.zoom,
        sourceFilter: state.sourceFilter,
      }),
    },
  ),
);
