import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { SearchMode, SearchResult, SearchFacet } from "@/types/search";

export interface SearchFilter {
  key: string;
  label: string;
  value: string | string[];
  type: "text" | "select" | "date" | "number" | "boolean";
}

export interface SavedSearch {
  id: string;
  name: string;
  query: string;
  mode: SearchMode;
  filters: SearchFilter[];
  created_at: number;
  pinned: boolean;
}

export interface SearchHistoryEntry {
  query: string;
  mode: SearchMode;
  timestamp: number;
  result_count: number;
}

export interface SearchState {
  query: string;
  mode: SearchMode;
  filters: SearchFilter[];
  results: SearchResult[];
  facets: SearchFacet[];
  total: number;
  tookMs: number;
  page: number;
  pageSize: number;
  maxScore: number;
  isLoading: boolean;
  error: string | null;
  selectedResult: SearchResult | null;
  previewOpen: boolean;
  activeTab: "all" | "cases" | "evidence" | "entities" | "timeline" | "kg" | "reports";
  savedSearches: SavedSearch[];
  searchHistory: SearchHistoryEntry[];
  showFilters: boolean;
  showSuggestions: boolean;
  showHistory: boolean;

  setQuery: (query: string) => void;
  setMode: (mode: SearchMode) => void;
  setFilters: (filters: SearchFilter[]) => void;
  addFilter: (filter: SearchFilter) => void;
  removeFilter: (key: string) => void;
  clearFilters: () => void;
  setSearchResults: (response: {
    results: SearchResult[];
    facets: SearchFacet[];
    total: number;
    took_ms: number;
    max_score: number;
  }) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPage: (page: number) => void;
  selectResult: (result: SearchResult | null) => void;
  setPreviewOpen: (open: boolean) => void;
  setActiveTab: (tab: SearchState["activeTab"]) => void;
  saveSearch: (name: string) => void;
  deleteSavedSearch: (id: string) => void;
  togglePinSavedSearch: (id: string) => void;
  loadSavedSearch: (id: string) => void;
  addToHistory: (resultCount: number) => void;
  clearHistory: () => void;
  setShowFilters: (show: boolean) => void;
  setShowSuggestions: (show: boolean) => void;
  setShowHistory: (show: boolean) => void;
  reset: () => void;
}

let _nextId = 1;
function uid(): string {
  return `${Date.now()}-${_nextId++}`;
}

const INITIAL_STATE = {
  query: "",
  mode: "hybrid" as SearchMode,
  filters: [] as SearchFilter[],
  results: [] as SearchResult[],
  facets: [] as SearchFacet[],
  total: 0,
  tookMs: 0,
  page: 1,
  pageSize: 20,
  maxScore: 0,
  isLoading: false,
  error: null as string | null,
  selectedResult: null as SearchResult | null,
  previewOpen: false,
  activeTab: "all" as SearchState["activeTab"],
  showFilters: false,
  showSuggestions: false,
  showHistory: false,
};

export const useSearchStore = create<SearchState>()(
  persist(
    (set, get) => ({
      ...INITIAL_STATE,
      savedSearches: [],
      searchHistory: [],

      setQuery: (query) => set({ query, page: 1 }),
      setMode: (mode) => set({ mode, page: 1 }),
      setFilters: (filters) => set({ filters, page: 1 }),
      addFilter: (filter) =>
        set((s) => ({
          filters: [...s.filters.filter((f) => f.key !== filter.key), filter],
          page: 1,
        })),
      removeFilter: (key) =>
        set((s) => ({
          filters: s.filters.filter((f) => f.key !== key),
          page: 1,
        })),
      clearFilters: () => set({ filters: [], page: 1 }),

      setSearchResults: (response) =>
        set({
          results: response.results ?? [],
          facets: response.facets ?? [],
          total: response.total ?? 0,
          tookMs: response.took_ms ?? 0,
          maxScore: response.max_score ?? 0,
          isLoading: false,
          error: null,
        }),

      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error, isLoading: false }),
      setPage: (page) => set({ page }),

      selectResult: (result) => set({ selectedResult: result, previewOpen: !!result }),
      setPreviewOpen: (open) => set({ previewOpen: open, selectedResult: open ? get().selectedResult : null }),

      setActiveTab: (activeTab) => set({ activeTab }),

      saveSearch: (name) => {
        const s = get();
        const saved: SavedSearch = {
          id: uid(),
          name,
          query: s.query,
          mode: s.mode,
          filters: [...s.filters],
          created_at: Date.now(),
          pinned: false,
        };
        set((prev) => ({ savedSearches: [saved, ...prev.savedSearches] }));
      },

      deleteSavedSearch: (id) =>
        set((s) => ({ savedSearches: s.savedSearches.filter((ss) => ss.id !== id) })),

      togglePinSavedSearch: (id) =>
        set((s) => ({
          savedSearches: s.savedSearches.map((ss) =>
            ss.id === id ? { ...ss, pinned: !ss.pinned } : ss,
          ),
        })),

      loadSavedSearch: (id) => {
        const ss = get().savedSearches.find((s) => s.id === id);
        if (ss) {
          set({
            query: ss.query,
            mode: ss.mode,
            filters: [...ss.filters],
            page: 1,
          });
        }
      },

      addToHistory: (resultCount) => {
        const s = get();
        if (!s.query || !s.query.trim()) return;
        const entry: SearchHistoryEntry = {
          query: s.query,
          mode: s.mode,
          timestamp: Date.now(),
          result_count: resultCount,
        };
        const filtered = get().searchHistory.filter(
          (h) => h.query !== s.query || h.mode !== s.mode,
        );
        set({ searchHistory: [entry, ...filtered].slice(0, 100) });
      },

      clearHistory: () => set({ searchHistory: [] }),

      setShowFilters: (showFilters) => set({ showFilters }),
      setShowSuggestions: (showSuggestions) => set({ showSuggestions }),
      setShowHistory: (showHistory) => set({ showHistory }),

      reset: () =>
        set({
          ...INITIAL_STATE,
          savedSearches: get().savedSearches,
          searchHistory: get().searchHistory,
        }),
    }),
    {
      name: "crimekit-search",
      partialize: (state) => ({
        savedSearches: state.savedSearches,
        searchHistory: state.searchHistory.slice(0, 50),
        mode: state.mode,
      }),
      merge: (persisted, current) => {
        const p = persisted as Record<string, unknown> | null;
        return {
          ...current,
          ...(p ?? {}),
          query: typeof p?.query === "string" ? p.query : current.query,
          mode: typeof p?.mode === "string" ? (p.mode as SearchMode) : current.mode,
        };
      },
    },
  ),
);
