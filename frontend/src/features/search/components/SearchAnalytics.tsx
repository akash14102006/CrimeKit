"use client";

import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  BarChart3,
  Layers,
  Brain,
} from "lucide-react";
import { useSearchStore } from "../store/searchStore";

export function SearchAnalytics() {
  const { results, total, tookMs, facets, maxScore, mode } = useSearchStore();

  const categoryCounts: Record<string, number> = {};
  for (const r of results) {
    categoryCounts[r.type] = (categoryCounts[r.type] || 0) + 1;
  }

  const avgScore =
    results.length > 0
      ? results.reduce((sum, r) => sum + r.score, 0) / results.length
      : 0;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <BarChart3 className="h-3.5 w-3.5 text-muted-foreground" />
        <span className="text-xs font-medium">Search Analytics</span>
      </div>

      {total > 0 ? (
        <ScrollArea className="max-h-[400px]">
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2 rounded bg-muted/50 text-center">
                <div className="text-lg font-bold">{total}</div>
                <div className="text-[10px] text-muted-foreground">Total Results</div>
              </div>
              <div className="p-2 rounded bg-muted/50 text-center">
                <div className="text-lg font-bold">{tookMs}ms</div>
                <div className="text-[10px] text-muted-foreground">Search Time</div>
              </div>
              <div className="p-2 rounded bg-muted/50 text-center">
                <div className="text-lg font-bold">{results.length}</div>
                <div className="text-[10px] text-muted-foreground">Page Results</div>
              </div>
              <div className="p-2 rounded bg-muted/50 text-center">
                <div className="text-lg font-bold">{(avgScore * 100).toFixed(0)}%</div>
                <div className="text-[10px] text-muted-foreground">Avg Relevance</div>
              </div>
            </div>

            <div className="p-2 rounded border space-y-2">
              <div className="flex items-center gap-2 text-xs font-medium">
                <Layers className="h-3 w-3" />
                Search Mode
              </div>
              <Badge variant="outline" className="text-[10px] capitalize">
                {mode}
              </Badge>
            </div>

            {Object.keys(categoryCounts).length > 0 && (
              <div className="p-2 rounded border space-y-2">
                <div className="text-xs font-medium">Results by Category</div>
                <div className="space-y-1.5">
                  {Object.entries(categoryCounts)
                    .sort(([, a], [, b]) => b - a)
                    .map(([type, count]) => (
                      <div key={type} className="flex items-center gap-2">
                        <span className="text-[10px] text-muted-foreground capitalize flex-1">
                          {type}
                        </span>
                        <div className="h-1.5 flex-1 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full"
                            style={{
                              width: `${(count / results.length) * 100}%`,
                            }}
                          />
                        </div>
                        <span className="text-[10px] font-medium w-6 text-right">
                          {count}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {facets && facets.length > 0 && (
              <div className="p-2 rounded border space-y-2">
                <div className="text-xs font-medium">Facets</div>
                {facets.slice(0, 5).map((facet) => (
                  <div key={facet.name} className="space-y-1">
                    <div className="text-[10px] text-muted-foreground">
                      {facet.name}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {facet.buckets.slice(0, 5).map((b) => (
                        <Badge
                          key={b.value}
                          variant="outline"
                          className="text-[9px]"
                        >
                          {b.value}: {b.count}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {maxScore > 0 && (
              <div className="p-2 rounded border space-y-1">
                <div className="flex items-center gap-2 text-xs font-medium">
                  <Brain className="h-3 w-3" />
                  Confidence Distribution
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full"
                    style={{ width: `${maxScore * 100}%` }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-muted-foreground">
                  <span>0%</span>
                  <span>Max: {(maxScore * 100).toFixed(0)}%</span>
                  <span>100%</span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      ) : (
        <div className="text-center py-6">
          <BarChart3 className="h-6 w-6 mx-auto text-muted-foreground/30 mb-2" />
          <p className="text-[10px] text-muted-foreground">
            Run a search to see analytics.
          </p>
        </div>
      )}
    </div>
  );
}
