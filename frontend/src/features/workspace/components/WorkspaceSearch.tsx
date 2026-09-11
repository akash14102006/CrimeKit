"use client";

import { useState, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Search, X, FileSearch } from "lucide-react";
import { useGlobalSearch } from "@/hooks/queries/useGlobalSearch";
import { useWorkspaceStore } from "@/store/workspaceStore";
import type { SearchResult } from "@/types/search";

interface Props {
  caseId: string;
}

export function WorkspaceSearch({ caseId: _caseId }: Props) { // eslint-disable-line @typescript-eslint/no-unused-vars
  const [query, setQuery] = useState("");
  const { setSearch } = useWorkspaceStore();
  const searchRequest = query.length >= 2 ? { query } : { query: "" };
  const { data: searchResponse, isLoading } = useGlobalSearch(searchRequest);
  const results = searchResponse?.results ?? [];

  const handleSearch = useCallback(
    (value: string) => {
      setQuery(value);
      if (value.length >= 2) {
        setSearch(value);
      }
    },
    [setSearch],
  );

  const clearSearch = useCallback(() => {
    setQuery("");
    setSearch("");
  }, [setSearch]);

  return (
    <div className="space-y-2 p-3">
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
        <Input
          placeholder="Search evidence, people, locations..."
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          className="h-8 pl-8 pr-8 text-xs"
        />
        {query && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-1 top-1 h-6 w-6 p-0"
            onClick={clearSearch}
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>

      {query.length >= 2 && (
        <ScrollArea className="h-48">
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : results.length > 0 ? (
            <div className="space-y-1">
              {results.map((item: SearchResult, i: number) => (
                <div
                  key={i}
                  className="flex items-center gap-2 text-xs py-1.5 px-2 rounded hover:bg-muted cursor-pointer"
                  onClick={() => {
                    if (item.type === "evidence" && item.id) {
                      useWorkspaceStore.getState().setSelectedEvidenceId(item.id);
                    }
                  }}
                >
                  <FileSearch className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                  <span className="truncate flex-1">{item.title ?? `Result ${i + 1}`}</span>
                  {item.type && (
                    <Badge variant="outline" className="text-[10px]">{item.type}</Badge>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground text-center py-4">No results found</p>
          )}
        </ScrollArea>
      )}
    </div>
  );
}
