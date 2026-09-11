import { useQuery } from "@tanstack/react-query";
import { timelineService } from "@/services/timelineService";
import type { TimelineEvent, TimelineQuery } from "@/types/timeline";

export function useCaseTimeline(caseId?: string) {
  return useQuery({
    queryKey: ["timeline", "case", caseId],
    queryFn: () => timelineService.list({ case_id: caseId }),
    enabled: !!caseId,
  });
}

export function useTimeline(params?: TimelineQuery) {
  return useQuery({
    queryKey: ["timeline", params],
    queryFn: () => timelineService.list(params),
  });
}

export type { TimelineEvent, TimelineQuery };
