"use client";

import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { FileText, ExternalLink, Hash } from "lucide-react";
import { useWorkspaceEvidence } from "@/hooks/queries/useWorkspace";

export function EvidenceReferencesPanel({ caseId }: { caseId: string }) {
  const { data: evidence, isLoading } = useWorkspaceEvidence(caseId);

  if (isLoading) {
    return (
      <div className="space-y-3 p-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b">
        <FileText className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold">Evidence References</h3>
        {evidence && evidence.length > 0 && (
          <Badge variant="secondary" className="text-[10px]">
            {evidence.length}
          </Badge>
        )}
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-2">
          {!evidence || evidence.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 mx-auto text-muted-foreground/20 mb-3" />
              <h4 className="text-sm font-medium mb-1">No Evidence</h4>
              <p className="text-xs text-muted-foreground max-w-xs mx-auto">
                Upload evidence files to this case to enable AI analysis and
                cross-referencing.
              </p>
            </div>
          ) : (
            evidence.map((item) => (
              <div
                key={item.id}
                className="rounded-lg border p-3 space-y-1.5 hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <FileText className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    <span className="text-xs font-medium truncate">
                      {item.filename}
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 shrink-0"
                    onClick={() =>
                      window.open(`/evidence/${item.id}`, "_blank")
                    }
                  >
                    <ExternalLink className="h-3 w-3" />
                  </Button>
                </div>
                <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Hash className="h-2.5 w-2.5" />
                    <span className="font-mono">{item.sha256.slice(0, 12)}...</span>
                  </div>
                  {item.custody_entries != null && (
                    <span>{item.custody_entries} custody entries</span>
                  )}
                  {item.has_document && (
                    <Badge variant="outline" className="text-[9px]">
                      Text extracted
                    </Badge>
                  )}
                </div>
                {item.ai_score != null && (
                  <div className="h-1 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary/60 rounded-full"
                      style={{ width: `${item.ai_score * 100}%` }}
                    />
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
