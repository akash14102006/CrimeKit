"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Search,
  X,
  Clock,
  Loader2,
  SlidersHorizontal,
  Sparkles,
} from "lucide-react";
import { useSearchStore } from "../store/searchStore";
import { useDebounce } from "@/hooks/useDebounce";

const SEARCH_MODES = [
  { value: "hybrid", label: "Hybrid", description: "Best combined results" },
  { value: "semantic", label: "Semantic", description: "Meaning-based search" },
  { value: "keyword", label: "Keyword", description: "Exact text matching" },
];

export function SearchBar() {
  const {
    query,
    setQuery,
    mode,
    setMode,
    showFilters,
    setShowFilters,
    showHistory,
    setShowHistory,
    searchHistory,
    isLoading,
  } = useSearchStore();

  const [localQuery, setLocalQuery] = useState(query);
  const [showModes, setShowModes] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const debouncedLocalQuery = useDebounce(localQuery, 300);

  useEffect(() => {
    setQuery(debouncedLocalQuery);
  }, [debouncedLocalQuery, setQuery]);

  const handleChange = useCallback(
    (value: string) => {
      setLocalQuery(value);
    },
    [],
  );

  const handleClear = useCallback(() => {
    setLocalQuery("");
    setQuery("");
    inputRef.current?.focus();
  }, [setQuery]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Escape") {
        handleClear();
      }
    },
    [handleClear],
  );

  const handleHistorySelect = useCallback(
    (q: string) => {
      setLocalQuery(q);
      setQuery(q);
      setShowHistory(false);
    },
    [setQuery, setShowHistory],
  );

  const currentMode = SEARCH_MODES.find((m) => m.value === mode) || SEARCH_MODES[0];

  return (
    <div className="relative">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            ref={inputRef}
            value={localQuery}
            onChange={(e) => handleChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search cases, evidence, entities, timeline, reports..."
            className="pl-10 pr-10 h-11 text-sm"
            aria-label="Search"
            onFocus={() => {
              if (localQuery && searchHistory.length > 0) {
                setShowHistory(true);
              }
            }}
          />
          {localQuery && (
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-2 top-1/2 -translate-y-1/2 h-6 w-6 p-0"
              onClick={handleClear}
            >
              <X className="h-3.5 w-3.5" />
            </Button>
          )}
          {isLoading && (
            <Loader2 className="absolute right-10 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-primary" />
          )}
        </div>

        <div className="relative">
          <Button
            variant="outline"
            size="sm"
            className="h-11 gap-2 text-xs"
            onClick={() => setShowModes(!showModes)}
          >
            <Sparkles className="h-3.5 w-3.5" />
            {currentMode.label}
          </Button>
          {showModes && (
            <div className="absolute right-0 top-full mt-1 z-50 bg-background border rounded-lg shadow-lg p-1 min-w-[200px]">
              {SEARCH_MODES.map((m) => (
                <button
                  key={m.value}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                    mode === m.value
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  }`}
                  onClick={() => {
                    setMode(m.value as typeof mode);
                    setShowModes(false);
                  }}
                >
                  <div className="font-medium">{m.label}</div>
                  <div className="text-[10px] opacity-70">{m.description}</div>
                </button>
              ))}
            </div>
          )}
        </div>

        <Button
          variant={showFilters ? "default" : "outline"}
          size="sm"
          className="h-11 gap-2 text-xs"
          onClick={() => setShowFilters(!showFilters)}
        >
          <SlidersHorizontal className="h-3.5 w-3.5" />
          Filters
        </Button>
      </div>

      {showHistory && searchHistory.length > 0 && !localQuery && (
        <div className="absolute left-0 right-0 top-full mt-1 z-50 bg-background border rounded-lg shadow-lg max-h-60 overflow-auto">
          <div className="p-2">
            <div className="flex items-center justify-between px-2 py-1">
              <span className="text-[10px] text-muted-foreground font-medium">
                Recent Searches
              </span>
              <Button
                variant="ghost"
                size="sm"
                className="h-5 text-[10px]"
                onClick={() => setShowHistory(false)}
              >
                Clear
              </Button>
            </div>
            {searchHistory.slice(0, 10).map((h, i) => (
              <button
                key={`${h.query}-${i}`}
                className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-sm hover:bg-muted transition-colors"
                onClick={() => handleHistorySelect(h.query)}
              >
                <Clock className="h-3 w-3 text-muted-foreground shrink-0" />
                <span className="truncate flex-1 text-left">{h.query}</span>
                <Badge variant="outline" className="text-[9px] shrink-0">
                  {h.result_count} results
                </Badge>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
