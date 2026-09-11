import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { searchService } from "@/services/searchService";
import type {
  GeneralSearchRequest,
  SearchResponse,
} from "@/types/search";

export function useGlobalSearch(request: GeneralSearchRequest) {
  return useQuery({
    queryKey: ["search", request],
    queryFn: () => searchService.query(request),
    enabled: !!request.query,
  });
}

export function useSearchReindex() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => searchService.reindex(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["search"] }),
  });
}

export type { SearchResponse, GeneralSearchRequest };
