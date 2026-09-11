"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Search,
  Bookmark,
  Clock,
  BarChart3,
  RefreshCw,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { SearchBar } from "../components/SearchBar";
import { AdvancedFilters } from "../components/AdvancedFilters";
import { SearchResultCard } from "../components/SearchResultCard";
import { SearchPreview } from "../components/SearchPreview";
import { SavedSearches } from "../components/SavedSearches";
import { SearchHistory } from "../components/SearchHistory";
import { SearchAnalytics } from "../components/SearchAnalytics";
import { useUnifiedSearch } from "../hooks/useSearch";
import { useSearchStore } from "../store/searchStore";

function SearchContent() {
  const searchParams = useSearchParams();
  const urlQuery = searchParams.get("q") || "";

  const search = useUnifiedSearch();
  const {
    query,
    results,
    total,
    tookMs,
    isLoading,
    error,
    activeTab,
    setActiveTab,
    previewOpen,
  } = useSearchStore();

  const tabCounts = {
    all: results.length,
    cases: results.filter((r) => r.type === "case").length,
    evidence: results.filter((r) => r.type === "evidence").length,
    entities: results.filter((r) => r.type === "entity").length,
    timeline: results.filter((r) => r.type === "timeline").length,
    kg: results.filter((r) => r.type === "entity" || r.type === "relationship").length,
    reports: results.filter((r) => r.type === "report").length,
  };

  const filteredResults =
    activeTab === "all"
      ? results
      : results.filter((r) => {
          switch (activeTab) {
            case "cases":
              return r.type === "case";
            case "evidence":
              return r.type === "evidence";
            case "entities":
              return r.type === "entity";
            case "timeline":
              return r.type === "timeline";
            case "kg":
              return r.type === "entity" || r.type === "relationship";
            case "reports":
              return r.type === "report";
            default:
              return true;
          }
        });

  const [sideTab, setSideTab] = useState<
    "results" | "saved" | "history" | "analytics"
  >("results");

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <div className="flex-1 flex flex-col min-w-0">
        <div className="px-6 py-4 border-b space-y-4">
          <div className="flex items-center gap-3">
            <Search className="h-5 w-5 text-primary" />
            <h1 className="text-lg font-semibold">Enterprise Search</h1>
            {total > 0 && (
              <Badge variant="secondary" className="text-[10px]">
                {total.toLocaleString()} results in {tookMs}ms
              </Badge>
            )}
          </div>
          <SearchBar />
          <AdvancedFilters />
        </div>

        <div className="flex-1 flex min-h-0">
          <div className="flex-1 flex flex-col min-w-0">
            <div className="flex items-center gap-1 px-4 py-2 border-b">
              {(
                [
                  { key: "results" as const, icon: <Search className="h-3 w-3" />, label: "Results" },
                  { key: "saved" as const, icon: <Bookmark className="h-3 w-3" />, label: "Saved" },
                  { key: "history" as const, icon: <Clock className="h-3 w-3" />, label: "History" },
                  { key: "analytics" as const, icon: <BarChart3 className="h-3 w-3" />, label: "Analytics" },
                ] as const
              ).map((tab) => (
                <button
                  key={tab.key}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-xs transition-colors ${
                    sideTab === tab.key
                      ? "bg-muted font-medium"
                      : "text-muted-foreground hover:bg-muted/50"
                  }`}
                  onClick={() => setSideTab(tab.key)}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </div>

            {sideTab === "results" && (
              <div className="flex-1 overflow-hidden">
                {isLoading ? (
                  <div className="flex flex-col items-center justify-center h-full">
                    <Loader2 className="h-8 w-8 animate-spin text-primary mb-3" />
                    <p className="text-sm text-muted-foreground">Searching...</p>
                  </div>
                ) : error ? (
                  <div className="flex flex-col items-center justify-center h-full">
                    <AlertTriangle className="h-8 w-8 text-destructive mb-3" />
                    <p className="text-sm text-destructive mb-2">{error}</p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => search.refetch()}
                    >
                      <RefreshCw className="h-3.5 w-3.5 mr-1" />
                      Retry
                    </Button>
                  </div>
                ) : !(query && query.trim()) ? (
                  <div className="flex flex-col items-center justify-center h-full">
                    <Search className="h-16 w-16 text-muted-foreground/20 mb-4" />
                    <h3 className="text-lg font-semibold mb-2">
                      Enterprise Search
                    </h3>
                    <p className="text-sm text-muted-foreground max-w-md text-center mb-6">
                      Search across cases, evidence, entities, timeline events,
                      knowledge graph, reports, and more. All powered by the
                      backend search engine.
                    </p>
                    <div className="grid grid-cols-3 gap-3 max-w-lg">
                      {[
                        { label: "Cases", desc: "Search by title, status, description" },
                        { label: "Evidence", desc: "Search by filename, hash, metadata" },
                        { label: "Entities", desc: "People, organizations, devices" },
                        { label: "Timeline", desc: "Events, dates, actions" },
                        { label: "Knowledge Graph", desc: "Nodes, relationships, communities" },
                        { label: "AI Findings", desc: "Insights, patterns, anomalies" },
                      ].map((item) => (
                        <div
                          key={item.label}
                          className="p-3 rounded-lg border text-center"
                        >
                          <div className="text-xs font-medium mb-1">
                            {item.label}
                          </div>
                          <div className="text-[10px] text-muted-foreground">
                            {item.desc}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : filteredResults.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full">
                    <Search className="h-12 w-12 text-muted-foreground/20 mb-3" />
                    <h4 className="text-sm font-medium mb-1">No Results</h4>
                    <p className="text-xs text-muted-foreground max-w-xs text-center">
                      No results found for &quot;{query}&quot;. Try different keywords or
                      adjust filters.
                    </p>
                  </div>
                ) : (
                  <ScrollArea className="h-full">
                    <div className="p-4 space-y-2">
                      {filteredResults.map((result, i) => (
                        <SearchResultCard
                          key={`${result.type}-${result.id}-${i}`}
                          result={result}
                        />
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </div>
            )}

            {sideTab === "saved" && (
              <ScrollArea className="flex-1">
                <div className="p-4">
                  <SavedSearches />
                </div>
              </ScrollArea>
            )}

            {sideTab === "history" && (
              <ScrollArea className="flex-1">
                <div className="p-4">
                  <SearchHistory />
                </div>
              </ScrollArea>
            )}

            {sideTab === "analytics" && (
              <ScrollArea className="flex-1">
                <div className="p-4">
                  <SearchAnalytics />
                </div>
              </ScrollArea>
            )}
          </div>

          {previewOpen && <SearchPreview />}
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <AuthGuard
      allowedRoles={[
        "admin",
        "investigator",
        "analyst",
        "evidence_officer",
        "compliance_officer",
        "auditor",
        "viewer",
      ]}
    >
      <Suspense
        fallback={
          <div className="flex h-[400px] items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        }
      >
        <SearchContent />
      </Suspense>
    </AuthGuard>
  );
}
