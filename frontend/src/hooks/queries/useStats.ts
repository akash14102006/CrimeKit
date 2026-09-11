import { useQuery } from "@tanstack/react-query";
import { healthService } from "@/services/healthService";
import { processingService } from "@/services/processingService";

export function useQueueStats() {
  return useQuery({
    queryKey: ["queue", "stats"],
    queryFn: () => processingService.queueStats(),
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ["health", "detailed"],
    queryFn: () => healthService.detailed(),
  });
}

export function useLiveness() {
  return useQuery({
    queryKey: ["health", "live"],
    queryFn: () => healthService.live(),
  });
}
