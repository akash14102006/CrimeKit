import { useQuery } from "@tanstack/react-query";
import { healthService } from "@/services/healthService";
import { processingService } from "@/services/processingService";
import { useAuthStore } from "@/store/authStore";

export function useQueueStats() {
  const { isAuthenticated, sessionToken } = useAuthStore();
  return useQuery({
    queryKey: ["queue", "stats"],
    queryFn: () => processingService.queueStats(),
    enabled: isAuthenticated && !!sessionToken,
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
