"use client";

import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  Link2,
  ArrowRight,
  RefreshCw,
} from "lucide-react";
import { useWorkspace } from "@/hooks/queries/useWorkspace";

interface Props {
  caseId: string;
}

export function RelatedCasesPanel({ caseId }: Props) {
  const { data: workspace, isLoading, refetch } = useWorkspace(caseId);

  if (isLoading) {
    return (
      <div className="space-y-3 p-3">
        {Array.from({ length: 2 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  const similarCases = workspace?.similar_cases ?? [];
  const relatedEvidence = workspace?.related_evidence ?? [];

  return (
    <div className="space-y-3 p-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold flex items-center gap-1.5">
          <Link2 className="h-3.5 w-3.5" />
          Related
        </h4>
        <Button variant="ghost" size="sm" className="h-6 px-2" onClick={() => refetch()}>
          <RefreshCw className="h-3 w-3" />
        </Button>
      </div>

      {similarCases.length > 0 && (
        <div className="space-y-1">
          <span className="text-[10px] font-medium text-muted-foreground uppercase">Similar Cases</span>
          {similarCases.map((sc, i) => (
            <div key={i} className="p-2 rounded-md border text-xs space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-medium truncate flex-1">{sc.title}</span>
                <Badge variant="outline" className="text-[10px] ml-2">
                  {(sc.similarity * 100).toFixed(0)}%
                </Badge>
              </div>
              {sc.reason && (
                <p className="text-[10px] text-muted-foreground">{sc.reason}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {relatedEvidence.length > 0 && (
        <div className="space-y-1">
          <span className="text-[10px] font-medium text-muted-foreground uppercase">Related Evidence</span>
          {relatedEvidence.slice(0, 10).map((re, i) => (
            <div key={i} className="flex items-center gap-2 text-xs py-1">
              <span className="truncate">{re.evidence_id.slice(0, 8)}...</span>
              <ArrowRight className="h-3 w-3 shrink-0 text-muted-foreground" />
              <span className="truncate">{re.related_evidence_id.slice(0, 8)}...</span>
              <Badge variant="outline" className="text-[10px] ml-auto">
                {(re.similarity * 100).toFixed(0)}%
              </Badge>
            </div>
          ))}
        </div>
      )}

      {similarCases.length === 0 && relatedEvidence.length === 0 && (
        <div className="text-center py-4">
          <Link2 className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
          <p className="text-xs text-muted-foreground">No related cases found</p>
          <p className="text-[10px] text-muted-foreground mt-1">AI analysis will discover connections as evidence is processed</p>
        </div>
      )}
    </div>
  );
}
