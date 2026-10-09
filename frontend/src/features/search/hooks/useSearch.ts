import { useCallback, useRef, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { searchService } from "@/services/searchService";
import { useSearchStore } from "../store/searchStore";
import { useDebounce } from "@/hooks/useDebounce";
import type {
  GeneralSearchRequest,
  SemanticSearchRequest,
  EntitySearchRequest,
  SearchResponse,
} from "@/types/search";

export function useUnifiedSearch() {
  const {
    query,
    mode,
    filters,
    page,
    pageSize,
    setSearchResults,
    setLoading,
    setError,
    addToHistory,
  } = useSearchStore();

  const debouncedQuery = useDebounce(query, 300);
  const abortRef = useRef<AbortController | null>(null);

  const filterDict: Record<string, unknown> = {};
  for (const f of filters) {
    filterDict[f.key] = f.value;
  }

  const request: GeneralSearchRequest = {
    query: debouncedQuery,
    mode,
    filters: Object.keys(filterDict).length > 0 ? filterDict : undefined,
    page,
    page_size: pageSize,
  };

  const queryResult = useQuery({
    queryKey: ["search", "unified", request],
    queryFn: async () => {
      return searchService.query(request);
    },
    enabled: !!(debouncedQuery && debouncedQuery.trim()),
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    setLoading(queryResult.isLoading || queryResult.isFetching);
  }, [queryResult.isLoading, queryResult.isFetching, setLoading]);

  useEffect(() => {
    if (queryResult.data) {
      setSearchResults(queryResult.data);
      addToHistory(queryResult.data.total);
    }
  }, [queryResult.data, setSearchResults, addToHistory]);

  useEffect(() => {
    if (queryResult.error) {
      const msg = queryResult.error instanceof Error ? queryResult.error.message : "Search failed";
      setError(msg);
    }
  }, [queryResult.error, setError]);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setLoading(false);
  }, [setLoading]);

  return {
    ...queryResult,
    cancel,
    debouncedQuery,
  };
}

export function useSemanticSearch() {
  const { query, page, pageSize, setSearchResults, setLoading, setError } =
    useSearchStore();

  const request: SemanticSearchRequest = {
    query,
    page,
    page_size: pageSize,
  };

  return useMutation({
    mutationFn: (payload: SemanticSearchRequest) =>
      searchService.semantic(payload),
    onSuccess: (data) => {
      if (Array.isArray(data)) {
        setSearchResults({
          results: data,
          facets: [],
          total: data.length,
          took_ms: 0,
          max_score: 0,
        });
      }
      setLoading(false);
    },
    onError: (error: unknown) => {
      const msg = error instanceof Error ? error.message : "Semantic search failed";
      setError(msg);
    },
  });
}

export function useEntitySearch() {
  return useMutation({
    mutationFn: (payload: EntitySearchRequest) =>
      searchService.searchEntities(payload),
  });
}

export function useTimelineSearch() {
  return useMutation({
    mutationFn: (payload: {
      event_type?: string;
      entity_ids?: string[];
      page?: number;
      page_size?: number;
    }) => searchService.searchTimeline(payload),
  });
}

export function useCrossCorrelationSearch() {
  return useMutation({
    mutationFn: (payload: { query: string; evidence_ids?: string[] }) =>
      searchService.crossCorrelate(payload),
  });
}

export function useSearchHealth() {
  return useQuery({
    queryKey: ["search", "health"],
    queryFn: () => searchService.health(),
    refetchInterval: 60000,
  });
}

export function useSearchFacets(searchType: string) {
  return useQuery({
    queryKey: ["search", "facets", searchType],
    queryFn: async () => {
      const { api } = await import("@/lib/api-client");
      const { API } = await import("@/constants/api-endpoints");
      return api.get(API.search.facets(searchType));
    },
    enabled: !!searchType,
  });
}

export function useSearchReindex() {
  return useMutation({
    mutationFn: () => searchService.reindex(),
  });
}
