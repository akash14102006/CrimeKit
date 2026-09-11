import { useMutation } from "@tanstack/react-query";
import { aiService } from "@/services/aiService";
import { useWorkspace, useWorkspaceProgress } from "@/hooks/queries/useWorkspace";
import { useQueueStats } from "@/hooks/queries/useStats";
import { useCaseTimeline } from "@/hooks/queries/useTimeline";
import { useCaseKnowledgeGraph } from "@/hooks/queries/useKnowledgeGraph";

export function useAIQuery() {
  return useMutation({
    mutationFn: (payload: { query: string; case_id?: string; top_k?: number }) =>
      aiService.query(payload),
  });
}

export function useCrossCorrelate() {
  return useMutation({
    mutationFn: (payload: {
      evidence_ids?: string[];
      case_id?: string;
      max_results?: number;
    }) => aiService.crossCorrelate(payload),
  });
}

export function useAIWorkspaceData(caseId?: string) {
  const workspace = useWorkspace(caseId);
  const queueStats = useQueueStats();
  const timeline = useCaseTimeline(caseId);
  const graph = useCaseKnowledgeGraph(caseId);
  const progress = useWorkspaceProgress(caseId);

  return {
    workspace: workspace.data,
    workspaceLoading: workspace.isLoading,
    queueStats: queueStats.data,
    timeline: timeline.data,
    graph: graph.data,
    progress: progress.data,
    isLoading:
      workspace.isLoading || queueStats.isLoading || timeline.isLoading || graph.isLoading,
  };
}
