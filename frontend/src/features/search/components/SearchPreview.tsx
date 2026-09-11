"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  X,
  ExternalLink,
  Copy,
  Clock,
  FileText,
  Briefcase,
  GitBranch,
  Brain,
  Shield,
} from "lucide-react";
import { useSearchStore } from "../store/searchStore";

const TYPE_ICONS: Record<string, React.ReactNode> = {
  case: <Briefcase className="h-4 w-4" />,
  evidence: <FileText className="h-4 w-4" />,
  entity: <GitBranch className="h-4 w-4" />,
  timeline: <Clock className="h-4 w-4" />,
  finding: <Brain className="h-4 w-4" />,
  report: <FileText className="h-4 w-4" />,
  compliance: <Shield className="h-4 w-4" />,
  audit: <Shield className="h-4 w-4" />,
};

export function SearchPreview() {
  const { selectedResult, previewOpen, setPreviewOpen } = useSearchStore();

  if (!previewOpen || !selectedResult) return null;

  const metadata = selectedResult.metadata || {};

  const handleCopy = () => {
    navigator.clipboard.writeText(selectedResult.id || selectedResult.title);
  };

  const getDetailUrl = (): string | null => {
    switch (selectedResult.type) {
      case "case":
        return `/cases/${selectedResult.id}`;
      case "evidence":
        return `/evidence/${selectedResult.id}`;
      case "timeline":
        return `/timeline`;
      case "entity":
        return `/graph`;
      default:
        return null;
    }
  };

  const detailUrl = getDetailUrl();

  return (
    <div className="w-[380px] border-l flex flex-col bg-background shrink-0">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          {TYPE_ICONS[selectedResult.type] || <FileText className="h-4 w-4" />}
          <h3 className="text-sm font-semibold">Preview</h3>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={handleCopy}>
            <Copy className="h-3.5 w-3.5" />
          </Button>
          {detailUrl && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0"
              onClick={() => window.open(detailUrl, "_blank")}
            >
              <ExternalLink className="h-3.5 w-3.5" />
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            onClick={() => setPreviewOpen(false)}
          >
            <X className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          <div>
            <Badge variant="outline" className="text-[10px] mb-2 capitalize">
              {selectedResult.type}
            </Badge>
            <h4 className="text-sm font-semibold mb-1">
              {selectedResult.title || selectedResult.id}
            </h4>
            <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
              <span>ID: {selectedResult.id}</span>
              {selectedResult.created_at && (
                <span>
                  Created: {new Date(selectedResult.created_at).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>

          {selectedResult.snippet && (
            <div>
              <h5 className="text-xs font-medium mb-1">Snippet</h5>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {selectedResult.snippet}
              </p>
            </div>
          )}

          {selectedResult.highlights && selectedResult.highlights.length > 0 && (
            <div>
              <h5 className="text-xs font-medium mb-1">Highlights</h5>
              <div className="space-y-1">
                {selectedResult.highlights.map((h, i) => (
                  <div key={i} className="p-2 bg-muted/50 rounded text-xs">
                    <span className="text-[10px] text-muted-foreground">{h.field}:</span>
                    <p
                      className="mt-0.5"
                      dangerouslySetInnerHTML={{ __html: h.snippet }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {Object.keys(metadata).length > 0 && (
            <div>
              <h5 className="text-xs font-medium mb-1">Metadata</h5>
              <div className="space-y-1">
                {Object.entries(metadata).slice(0, 15).map(([key, value]) => (
                  <div key={key} className="flex items-start gap-2 text-xs">
                    <span className="text-muted-foreground shrink-0">{key}:</span>
                    <span className="font-mono text-[10px] break-all">
                      {typeof value === "object"
                        ? JSON.stringify(value)
                        : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedResult.type === "evidence" && (
            <div>
              <h5 className="text-xs font-medium mb-1">Actions</h5>
              <div className="flex flex-wrap gap-1.5">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-[10px]"
                  onClick={() => window.open(`/evidence/${selectedResult.id}`, "_blank")}
                >
                  Open Evidence
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-[10px]"
                  onClick={() => {
                    if (metadata.sha256) {
                      navigator.clipboard.writeText(String(metadata.sha256));
                    }
                  }}
                >
                  Copy Hash
                </Button>
                {Boolean(metadata.case_id) && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-[10px]"
                    onClick={() =>
                      window.open(`/workspace/${String(metadata.case_id)}`, "_blank")
                    }
                  >
                    Open Workspace
                  </Button>
                )}
              </div>
            </div>
          )}

          {selectedResult.type === "case" && (
            <div>
              <h5 className="text-xs font-medium mb-1">Actions</h5>
              <div className="flex flex-wrap gap-1.5">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-[10px]"
                  onClick={() => window.open(`/cases/${selectedResult.id}`, "_blank")}
                >
                  Open Case
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-[10px]"
                  onClick={() =>
                    window.open(`/workspace/${selectedResult.id}`, "_blank")
                  }
                >
                  Open Workspace
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-[10px]"
                  onClick={() => window.open(`/timeline?case=${selectedResult.id}`, "_blank")}
                >
                  View Timeline
                </Button>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
