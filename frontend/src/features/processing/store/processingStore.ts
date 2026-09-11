"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  QueueStats,
  WorkerInfo,
  DistributedTask,
  DLQItem,
  QueueDepth,
  DistributedMetrics,
  DistributedTaskStatus,
} from "@/types/processing";

export type ProcessingTab =
  | "overview"
  | "running"
  | "completed"
  | "failed"
  | "workers"
  | "history"
  | "dlq"
  | "analytics";

export interface ProcessingFilter {
  key: string;
  label: string;
  value: string;
  type: "text" | "select" | "date";
}

interface ProcessingState {
  // Data
  queueStats: QueueStats | null;
  workers: WorkerInfo[];
  runningTasks: DistributedTask[];
  failedTasks: DistributedTask[];
  dlqItems: DLQItem[];
  queueDepth: QueueDepth | null;
  metrics: DistributedMetrics | null;
  processors: string[];

  // Selection
  selectedTask: DistributedTask | null;
  selectedWorker: WorkerInfo | null;
  drawerOpen: boolean;

  // UI
  activeTab: ProcessingTab;
  filters: ProcessingFilter[];
  showFilters: boolean;
  searchQuery: string;

  // Actions
  setQueueStats: (stats: QueueStats) => void;
  setWorkers: (workers: WorkerInfo[]) => void;
  setRunningTasks: (tasks: DistributedTask[]) => void;
  setFailedTasks: (tasks: DistributedTask[]) => void;
  setDlqItems: (items: DLQItem[]) => void;
  setQueueDepth: (depth: QueueDepth) => void;
  setMetrics: (metrics: DistributedMetrics) => void;
  setProcessors: (processors: string[]) => void;
  selectTask: (task: DistributedTask | null) => void;
  selectWorker: (worker: WorkerInfo | null) => void;
  setDrawerOpen: (open: boolean) => void;
  setActiveTab: (tab: ProcessingTab) => void;
  setFilters: (filters: ProcessingFilter[]) => void;
  addFilter: (filter: ProcessingFilter) => void;
  removeFilter: (key: string) => void;
  clearFilters: () => void;
  setShowFilters: (show: boolean) => void;
  setSearchQuery: (query: string) => void;
}

export const useProcessingStore = create<ProcessingState>()(
  persist(
    (set) => ({
      queueStats: null,
      workers: [],
      runningTasks: [],
      failedTasks: [],
      dlqItems: [],
      queueDepth: null,
      metrics: null,
      processors: [],

      selectedTask: null,
      selectedWorker: null,
      drawerOpen: false,

      activeTab: "overview",
      filters: [],
      showFilters: false,
      searchQuery: "",

      setQueueStats: (stats) => set({ queueStats: stats }),
      setWorkers: (workers) => set({ workers }),
      setRunningTasks: (tasks) => set({ runningTasks: tasks }),
      setFailedTasks: (tasks) => set({ failedTasks: tasks }),
      setDlqItems: (items) => set({ dlqItems: items }),
      setQueueDepth: (depth) => set({ queueDepth: depth }),
      setMetrics: (metrics) => set({ metrics }),
      setProcessors: (processors) => set({ processors }),
      selectTask: (task) => set({ selectedTask: task, drawerOpen: !!task }),
      selectWorker: (worker) => set({ selectedWorker: worker }),
      setDrawerOpen: (open) =>
        set((state) => ({
          drawerOpen: open,
          selectedTask: open ? state.selectedTask : null,
        })),
      setActiveTab: (tab) => set({ activeTab: tab }),
      setFilters: (filters) => set({ filters }),
      addFilter: (filter) =>
        set((state) => ({
          filters: [...state.filters.filter((f) => f.key !== filter.key), filter],
        })),
      removeFilter: (key) =>
        set((state) => ({
          filters: state.filters.filter((f) => f.key !== key),
        })),
      clearFilters: () => set({ filters: [] }),
      setShowFilters: (show) => set({ showFilters: show }),
      setSearchQuery: (query) => set({ searchQuery: query }),
    }),
    {
      name: "crimekit-processing-store",
      partialize: (state) => ({
        activeTab: state.activeTab,
      }),
    },
  ),
);
