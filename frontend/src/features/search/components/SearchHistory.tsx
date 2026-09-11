"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Clock, Trash2, Search } from "lucide-react";
import { useSearchStore } from "../store/searchStore";

export function SearchHistory() {
  const { searchHistory, clearHistory, setQuery } = useSearchStore();

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-xs font-medium">Search History</span>
          {searchHistory.length > 0 && (
            <Badge variant="secondary" className="text-[10px]">
              {searchHistory.length}
            </Badge>
          )}
        </div>
        {searchHistory.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 text-[10px] gap-1"
            onClick={clearHistory}
          >
            <Trash2 className="h-2.5 w-2.5" />
            Clear
          </Button>
        )}
      </div>

      <ScrollArea className="max-h-[300px]">
        <div className="space-y-1">
          {searchHistory.map((h, i) => (
            <button
              key={`${h.query}-${h.timestamp}-${i}`}
              className="w-full flex items-center gap-2 p-2 rounded-md hover:bg-muted/50 transition-colors text-left"
              onClick={() => setQuery(h.query)}
            >
              <Search className="h-3 w-3 text-muted-foreground shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-xs truncate">{h.query}</div>
                <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                  <span>{new Date(h.timestamp).toLocaleDateString()}</span>
                  <Badge variant="outline" className="text-[8px]">
                    {h.result_count} results
                  </Badge>
                </div>
              </div>
            </button>
          ))}

          {searchHistory.length === 0 && (
            <div className="text-center py-6">
              <Clock className="h-6 w-6 mx-auto text-muted-foreground/30 mb-2" />
              <p className="text-[10px] text-muted-foreground">
                No search history yet.
              </p>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
