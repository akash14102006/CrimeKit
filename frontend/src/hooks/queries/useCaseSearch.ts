import { useQuery } from "@tanstack/react-query";
import { searchService } from "@/services/searchService";
import type { CaseSearchRequest, SearchResponse } from "@/types/search";

export function useCaseSearch(request: CaseSearchRequest) {
  return useQuery({
    queryKey: ["cases", "search", request],
    queryFn: () => searchService.searchCases(request),
    enabled: true,
  });
}

export type { CaseSearchRequest, SearchResponse };
