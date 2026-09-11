import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  TSKArtifact,
  TSKFileInfo,
  TSKFilesystemInfo,
  TSKMetrics,
  TSKPartitionInfo,
  TSKProcessingStage,
  TSKTimelineEvent,
} from "@/types/tsk";

export type DiskAnalyzerView = "partitions" | "timeline" | "artifacts" | "entities" | "kg" | "provenance";
export type DiskAnalyzerPanelSize = "compact" | "normal" | "expanded";

interface DiskAnalyzerState {
  evidenceId: string | null;
  caseId: string | null;

  processing: boolean;
  processingStage: TSKProcessingStage | null;
  stagesCompleted: TSKProcessingStage[];
  stagesFailed: TSKProcessingStage[];
  progressPercent: number;
  jobId: string | null;

  partitions: TSKPartitionInfo[];
  filesystems: TSKFilesystemInfo[];
  files: TSKFileInfo[];
  artifacts: TSKArtifact[];
  timeline: TSKTimelineEvent[];
  metrics: TSKMetrics | null;

  selectedPartitionIndex: number | null;
  selectedFilesystemIndex: number | null;
  selectedFile: TSKFileInfo | null;
  selectedArtifact: TSKArtifact | null;

  activeView: DiskAnalyzerView;
  panelSize: DiskAnalyzerPanelSize;
  showDeleted: boolean;
  showUnallocated: boolean;
  fileFilter: string;

  errors: string[];

  setEvidenceId: (id: string) => void;
  setCaseId: (id: string) => void;
  setProcessing: (v: boolean) => void;
  setProcessingStage: (stage: TSKProcessingStage | null) => void;
  setStagesCompleted: (stages: TSKProcessingStage[]) => void;
  setStagesFailed: (stages: TSKProcessingStage[]) => void;
  setProgressPercent: (p: number) => void;
  setJobId: (id: string | null) => void;

  setPartitions: (p: TSKPartitionInfo[]) => void;
  setFilesystems: (fs: TSKFilesystemInfo[]) => void;
  setFiles: (f: TSKFileInfo[]) => void;
  setArtifacts: (a: TSKArtifact[]) => void;
  setTimeline: (t: TSKTimelineEvent[]) => void;
  setMetrics: (m: TSKMetrics | null) => void;
  setErrors: (e: string[]) => void;

  selectPartition: (index: number | null) => void;
  selectFilesystem: (index: number | null) => void;
  selectFile: (file: TSKFileInfo | null) => void;
  selectArtifact: (artifact: TSKArtifact | null) => void;

  setActiveView: (view: DiskAnalyzerView) => void;
  setPanelSize: (size: DiskAnalyzerPanelSize) => void;
  setShowDeleted: (v: boolean) => void;
  setShowUnallocated: (v: boolean) => void;
  setFileFilter: (filter: string) => void;

  loadPipelineResult: (result: {
    image_info?: unknown;
    volume_info?: { partitions?: TSKPartitionInfo[] } | null;
    filesystems?: TSKFilesystemInfo[];
    files?: TSKFileInfo[];
    artifacts?: TSKArtifact[];
    timeline?: TSKTimelineEvent[];
    metrics?: TSKMetrics;
    errors?: string[];
  }) => void;

  reset: () => void;
}

const initialState = {
  evidenceId: null as string | null,
  caseId: null as string | null,
  processing: false,
  processingStage: null as TSKProcessingStage | null,
  stagesCompleted: [] as TSKProcessingStage[],
  stagesFailed: [] as TSKProcessingStage[],
  progressPercent: 0,
  jobId: null as string | null,
  partitions: [] as TSKPartitionInfo[],
  filesystems: [] as TSKFilesystemInfo[],
  files: [] as TSKFileInfo[],
  artifacts: [] as TSKArtifact[],
  timeline: [] as TSKTimelineEvent[],
  metrics: null as TSKMetrics | null,
  selectedPartitionIndex: null as number | null,
  selectedFilesystemIndex: null as number | null,
  selectedFile: null as TSKFileInfo | null,
  selectedArtifact: null as TSKArtifact | null,
  activeView: "partitions" as DiskAnalyzerView,
  panelSize: "normal" as DiskAnalyzerPanelSize,
  showDeleted: true,
  showUnallocated: false,
  fileFilter: "",
  errors: [] as string[],
};

export const useDiskAnalyzerStore = create<DiskAnalyzerState>()(
  persist(
    (set) => ({
      ...initialState,

      setEvidenceId: (id) => set({ evidenceId: id }),
      setCaseId: (id) => set({ caseId: id }),
      setProcessing: (v) => set({ processing: v }),
      setProcessingStage: (stage) => set({ processingStage: stage }),
      setStagesCompleted: (stages) => set({ stagesCompleted: stages }),
      setStagesFailed: (stages) => set({ stagesFailed: stages }),
      setProgressPercent: (p) => set({ progressPercent: p }),
      setJobId: (id) => set({ jobId: id }),

      setPartitions: (p) => set({ partitions: p }),
      setFilesystems: (fs) => set({ filesystems: fs }),
      setFiles: (f) => set({ files: f }),
      setArtifacts: (a) => set({ artifacts: a }),
      setTimeline: (t) => set({ timeline: t }),
      setMetrics: (m) => set({ metrics: m }),
      setErrors: (e) => set({ errors: e }),

      selectPartition: (index) =>
        set({ selectedPartitionIndex: index, selectedFilesystemIndex: null, selectedFile: null }),
      selectFilesystem: (index) =>
        set({ selectedFilesystemIndex: index, selectedFile: null }),
      selectFile: (file) => set({ selectedFile: file }),
      selectArtifact: (artifact) => set({ selectedArtifact: artifact }),

      setActiveView: (view) => set({ activeView: view }),
      setPanelSize: (size) => set({ panelSize: size }),
      setShowDeleted: (v) => set({ showDeleted: v }),
      setShowUnallocated: (v) => set({ showUnallocated: v }),
      setFileFilter: (filter) => set({ fileFilter: filter }),

      loadPipelineResult: (result) =>
        set({
          partitions: result.volume_info?.partitions ?? [],
          filesystems: result.filesystems ?? [],
          files: result.files ?? [],
          artifacts: result.artifacts ?? [],
          timeline: result.timeline ?? [],
          metrics: result.metrics ?? null,
          errors: result.errors ?? [],
          processing: false,
          processingStage: "processing_complete",
        }),

      reset: () => set(initialState),
    }),
    {
      name: "crimekit-disk-analyzer",
      partialize: (state) => ({
        evidenceId: state.evidenceId,
        caseId: state.caseId,
        activeView: state.activeView,
        panelSize: state.panelSize,
        showDeleted: state.showDeleted,
        showUnallocated: state.showUnallocated,
      }),
    },
  ),
);
