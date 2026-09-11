"use client";

import { memo, useCallback } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  FileText,
  Briefcase,
  Clock,
  GitBranch,
  Brain,
  Shield,
  ExternalLink,
  Copy,
  Eye,
} from "lucide-react";
import { useSearchStore } from "../store/searchStore";
import type { SearchResult } from "@/types/search";

const TYPE_CONFIG: Record<
  string,
  { icon: React.ReactNode; color: string; label: string }
> = {
  case: { icon: <Briefcase className="h-3 w-3" />, color: "bg-blue-100 text-blue-700", label: "Case" },
  evidence: { icon: <FileText className="h-3 w-3" />, color: "bg-green-100 text-green-700", label: "Evidence" },
  entity: { icon: <GitBranch className="h-3 w-3" />, color: "bg-purple-100 text-purple-700", label: "Entity" },
  timeline: { icon: <Clock className="h-3 w-3" />, color: "bg-amber-100 text-amber-700", label: "Timeline" },
  document: { icon: <FileText className="h-3 w-3" />, color: "bg-cyan-100 text-cyan-700", label: "Document" },
  finding: { icon: <Brain className="h-3 w-3" />, color: "bg-pink-100 text-pink-700", label: "AI Finding" },
  report: { icon: <FileText className="h-3 w-3" />, color: "bg-indigo-100 text-indigo-700", label: "Report" },
  compliance: { icon: <Shield className="h-3 w-3" />, color: "bg-red-100 text-red-700", label: "Compliance" },
  audit: { icon: <Shield className="h-3 w-3" />, color: "bg-gray-100 text-gray-700", label: "Audit" },
};

function getDetailUrl(result: SearchResult): string | null {
  switch (result.type) {
    case "case":
      return `/cases/${result.id}`;
    case "evidence":
      return `/evidence/${result.id}`;
    case "timeline":
      return `/timeline`;
    case "entity":
      return `/graph`;
    case "finding":
    case "document":
      return result.metadata?.evidence_id
        ? `/evidence/${result.metadata.evidence_id}`
        : null;
    case "report":
      return result.metadata?.case_id
        ? `/workspace/${result.metadata.case_id}`
        : null;
    default:
      return null;
  }
}

function ScoreBar({ score }: { score: number }) {
  const percent = Math.round(score * 100);
  let color = "bg-green-500";
  if (percent < 30) color = "bg-red-500";
  else if (percent < 60) color = "bg-amber-500";

  return (
    <div className="flex items-center gap-1.5">
      <div className="h-1.5 w-12 bg-muted rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${percent}%` }} />
      </div>
      <span className="text-[10px] text-muted-foreground">{percent}%</span>
    </div>
  );
}

export const SearchResultCard = memo(function SearchResultCard({
  result,
}: {
  result: SearchResult;
}) {
  const { selectResult, selectedResult } = useSearchStore();
  const config = TYPE_CONFIG[result.type] || TYPE_CONFIG.document;
  const detailUrl = getDetailUrl(result);
  const isSelected = selectedResult?.id === result.id && selectedResult?.type === result.type;

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(result.id || result.title);
  }, [result]);

  return (
    <div
      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
        isSelected
          ? "border-primary bg-primary/5"
          : "hover:bg-muted/30"
      }`}
      onClick={() => selectResult(result)}
    >
      <div className="flex items-start gap-3">
        <div className={`p-1.5 rounded-md ${config.color} shrink-0`}>
          {config.icon}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className={`text-[9px] ${config.color}`}>
              {config.label}
            </Badge>
            <ScoreBar score={result.score} />
          </div>

          <h4 className="text-sm font-medium truncate">
            {result.title || result.id}
          </h4>

          {result.snippet && (
            <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
              {result.snippet}
            </p>
          )}

          {result.highlights && result.highlights.length > 0 && (
            <div className="mt-1.5 space-y-0.5">
              {result.highlights.slice(0, 2).map((h, i) => (
                <p
                  key={i}
                  className="text-[10px] text-muted-foreground"
                  dangerouslySetInnerHTML={{ __html: h.snippet }}
                />
              ))}
            </div>
          )}

          {result.created_at && (
            <div className="flex items-center gap-1 mt-1.5 text-[10px] text-muted-foreground">
              <Clock className="h-2.5 w-2.5" />
              {new Date(result.created_at).toLocaleDateString()}
            </div>
          )}
        </div>

        <div className="flex items-center gap-1 shrink-0">
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={(e) => {
              e.stopPropagation();
              selectResult(result);
            }}
          >
            <Eye className="h-3 w-3" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={(e) => {
              e.stopPropagation();
              handleCopy();
            }}
          >
            <Copy className="h-3 w-3" />
          </Button>
          {detailUrl && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                window.open(detailUrl, "_blank");
              }}
            >
              <ExternalLink className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
});
