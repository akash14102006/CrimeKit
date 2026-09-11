import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useDiskAnalyzerStore } from "../store/diskAnalyzerStore";
import { tskService } from "@/services/tskService";
import { evidenceService } from "@/services/evidenceService";
import { useEffect } from "react";
import type { TSKPipelineResult } from "@/types/tsk";

export function useTSKCapabilities() {
  return useQuery({
    queryKey: ["tsk", "capabilities"],
    queryFn: () => tskService.capabilities(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useEvidenceDetail(evidenceId: string | null) {
  return useQuery({
    queryKey: ["evidence", evidenceId],
    queryFn: () => evidenceService.detail(evidenceId!),
    enabled: !!evidenceId,
    staleTime: 30_000,
  });
}

export function useTSKProcess() {
  const queryClient = useQueryClient();
  const store = useDiskAnalyzerStore();

  return useMutation({
    mutationFn: (request: { evidence_id: string; case_id: string; sync?: boolean }) =>
      tskService.process(request),

    onMutate: () => {
      store.setProcessing(true);
      store.setProgressPercent(0);
      store.setErrors([]);
    },

    onSuccess: (data: TSKPipelineResult) => {
      store.loadPipelineResult(data);
      store.setJobId(data.job_id);
      store.setProgressPercent(100);
      queryClient.invalidateQueries({ queryKey: ["tsk"] });
    },

    onError: (error: Error) => {
      store.setProcessing(false);
      store.setErrors([error.message]);
    },
  });
}

export function useTSKEnqueue() {
  const store = useDiskAnalyzerStore();

  return useMutation({
    mutationFn: (request: { evidence_id: string; case_id: string; priority?: string }) =>
      tskService.enqueue(request),

    onMutate: () => {
      store.setProcessing(true);
      store.setProgressPercent(0);
    },

    onSuccess: (data) => {
      store.setJobId(data.job_id);
    },

    onError: (error: Error) => {
      store.setProcessing(false);
      store.setErrors([error.message]);
    },
  });
}

export function useTSKJobStatus(jobId: string | null, enabled = false) {
  const store = useDiskAnalyzerStore();

  const query = useQuery({
    queryKey: ["tsk", "status", jobId],
    queryFn: () => tskService.status(jobId!),
    enabled: enabled && !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed" || status === "cancelled") {
        return false;
      }
      return 2000;
    },
  });

  useEffect(() => {
    if (query.data) {
      const d = query.data;
      store.setProcessingStage(d.current_stage);
      store.setStagesCompleted(d.stages_completed);
      store.setStagesFailed(d.stages_failed);
      store.setProgressPercent(d.progress_percent);
      if (d.metrics) store.setMetrics(d.metrics);
      if (d.status === "completed" || d.status === "failed") {
        store.setProcessing(false);
      }
    }
  }, [query.data, store]);

  return query;
}

export function useFilteredFiles() {
  const { files, showDeleted, showUnallocated, fileFilter, selectedFilesystemIndex, filesystems } =
    useDiskAnalyzerStore();

  let filtered = files;

  if (selectedFilesystemIndex !== null && filesystems[selectedFilesystemIndex]) {
    const fs = filesystems[selectedFilesystemIndex];
    filtered = filtered.filter((f) => f.fs_type === fs.fs_type);
  }

  if (!showDeleted) {
    filtered = filtered.filter((f) => !f.is_deleted);
  }

  if (!showUnallocated) {
    filtered = filtered.filter((f) => f.allocation_state === "allocated");
  }

  if (fileFilter) {
    const lower = fileFilter.toLowerCase();
    filtered = filtered.filter(
      (f) =>
        f.name.toLowerCase().includes(lower) ||
        f.path.toLowerCase().includes(lower),
    );
  }

  return filtered;
}
