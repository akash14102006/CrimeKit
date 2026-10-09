"use client";

import { useEffect, useCallback, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { processingService, distributedService } from "@/services/processingService";
import { useProcessingStore } from "../store/processingStore";
import { useDebounce } from "@/hooks/useDebounce";
import { useAuthStore } from "@/store/authStore";
import type { DistributedTask, DistributedTaskStatus } from "@/types/processing";

export function useQueueStats() {
  const { setQueueStats } = useProcessingStore();
  const { isAuthenticated, sessionToken } = useAuthStore();

  return useQuery({
    queryKey: ["processing", "queue", "stats"],
    queryFn: async () => {
      const stats = await processingService.queueStats();
      setQueueStats(stats);
      return stats;
    },
    enabled: isAuthenticated && !!sessionToken,
    refetchInterval: isAuthenticated && !!sessionToken ? 5000 : false,
    staleTime: 3000,
  });
}

export function useWorkers() {
  const { setWorkers } = useProcessingStore();
  const { isAuthenticated, sessionToken } = useAuthStore();

  return useQuery({
    queryKey: ["processing", "workers"],
    queryFn: async () => {
      const response = await distributedService.workers();
      setWorkers(response.workers);
      return response;
    },
    enabled: isAuthenticated && !!sessionToken,
    refetchInterval: isAuthenticated && !!sessionToken ? 10000 : false,
    staleTime: 5000,
  });
}

export function useRunningTasks() {
  const { setRunningTasks, runningTasks } = useProcessingStore();
  const { isAuthenticated, sessionToken } = useAuthStore();

  const query = useQuery({
    queryKey: ["processing", "tasks", "running"],
    queryFn: async () => {
      const depth = await distributedService.queueDepth();
      return depth;
    },
    enabled: isAuthenticated && !!sessionToken,
    refetchInterval: isAuthenticated && !!sessionToken ? 5000 : false,
    staleTime: 3000,
  });

  return { ...query, tasks: runningTasks };
}

export function useFailedTasks() {
  const { setFailedTasks } = useProcessingStore();
  const { isAuthenticated, sessionToken } = useAuthStore();

  return useQuery({
    queryKey: ["processing", "tasks", "failed"],
    queryFn: async () => {
      const dlq = await distributedService.dlq();
      setFailedTasks(
        dlq.items.map((item) => ({
          id: item.task_id,
          processor_type: item.processor_type || "unknown",
          status: "FAILED" as DistributedTaskStatus,
          error: item.error,
          retry_count: item.retry_count,
          created_at: item.created_at,
        })),
      );
      return dlq;
    },
    enabled: isAuthenticated && !!sessionToken,
    refetchInterval: isAuthenticated && !!sessionToken ? 15000 : false,
    staleTime: 10000,
  });
}

export function useDLQ() {
  const { setDlqItems } = useProcessingStore();

  return useQuery({
    queryKey: ["processing", "dlq"],
    queryFn: async () => {
      const response = await distributedService.dlq();
      setDlqItems(response.items);
      return response;
    },
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

export function useQueueDepth() {
  const { setQueueDepth } = useProcessingStore();

  return useQuery({
    queryKey: ["processing", "queue", "depth"],
    queryFn: async () => {
      const depth = await distributedService.queueDepth();
      setQueueDepth(depth);
      return depth;
    },
    refetchInterval: 5000,
    staleTime: 3000,
  });
}

export function useMetrics() {
  const { setMetrics } = useProcessingStore();

  return useQuery({
    queryKey: ["processing", "metrics"],
    queryFn: async () => {
      const metrics = await distributedService.metrics();
      setMetrics(metrics);
      return metrics;
    },
    refetchInterval: 30000,
    staleTime: 15000,
  });
}

export function useProcessors() {
  const { setProcessors } = useProcessingStore();

  return useQuery({
    queryKey: ["processing", "processors"],
    queryFn: async () => {
      const response = await processingService.processors();
      setProcessors(response.processors);
      return response.processors;
    },
    staleTime: 60000,
  });
}

export function useTaskProgress(taskId: string | null) {
  return useQuery({
    queryKey: ["processing", "task", taskId, "progress"],
    queryFn: () => distributedService.taskProgress(taskId!),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (
        status === "COMPLETED" ||
        status === "FAILED" ||
        status === "CANCELLED" ||
        status === "DEAD_LETTERED"
      ) {
        return false;
      }
      return 2000;
    },
  });
}

export function useJobDetail(jobId: string | null) {
  return useQuery({
    queryKey: ["processing", "job", jobId],
    queryFn: () => distributedService.job(jobId!),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (
        status === "COMPLETED" ||
        status === "FAILED" ||
        status === "CANCELLED"
      ) {
        return false;
      }
      return 5000;
    },
  });
}

export function useCancelTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => distributedService.cancelTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["processing"] });
    },
  });
}

export function useRetryTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => distributedService.retryTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["processing"] });
    },
  });
}

export function useCancelJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: string) => distributedService.cancelJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["processing"] });
    },
  });
}

export function useResumeJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobId: string) => distributedService.resumeJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["processing"] });
    },
  });
}

export function useReplayDLQ() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => distributedService.dlqReplay(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["processing", "dlq"] });
    },
  });
}

export function usePurgeDLQ() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => distributedService.dlqPurge(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["processing", "dlq"] });
    },
  });
}

export function useEnqueueTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (task: {
      processor_type: string;
      payload?: Record<string, unknown>;
      priority?: number;
      dependencies?: string[];
    }) => distributedService.enqueueTask(task),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["processing"] });
    },
  });
}

export function useProcessingOverview() {
  const queueStats = useQueueStats();
  const workers = useWorkers();
  const queueDepth = useQueueDepth();
  const metrics = useMetrics();
  const processors = useProcessors();

  return {
    queueStats: queueStats.data,
    workers: workers.data?.workers ?? [],
    queueDepth: queueDepth.data,
    metrics: metrics.data,
    processors: processors.data ?? [],
    isLoading:
      queueStats.isLoading ||
      workers.isLoading ||
      queueDepth.isLoading ||
      metrics.isLoading,
    isError: queueStats.isError || workers.isError,
    refetch: () => {
      queueStats.refetch();
      workers.refetch();
      queueDepth.refetch();
      metrics.refetch();
    },
  };
}
