"use client";

import { FileText, ArrowRight, AlertTriangle, RefreshCw, Clock } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAllEvidence } from "@/hooks/queries/useEvidence";
import { useRBAC } from "@/hooks/useRBAC";
import { getErrorMessage } from "@/lib/api-client";

function EvidenceSkeleton() {
  return (
    <div className="flex items-center justify-between p-3 border rounded-lg">
      <div className="flex items-center space-x-3">
        <Skeleton className="h-8 w-8 rounded" />
        <div className="space-y-1">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-3 w-20" />
        </div>
      </div>
      <Skeleton className="h-5 w-16 rounded" />
    </div>
  );
}

function mimeToType(mime: string | null): string {
  if (!mime) return "unknown";
  const main = mime.split("/")[0];
  if (main === "image") return "Image";
  if (main === "video") return "Video";
  if (main === "audio") return "Audio";
  if (mime.includes("pdf")) return "PDF";
  if (mime.includes("zip") || mime.includes("archive")) return "Archive";
  if (mime.includes("text") || mime.includes("json") || mime.includes("xml")) return "Document";
  return "File";
}

export function RecentEvidence() {
  const { data: response, isLoading, isError, error, refetch } = useAllEvidence({ page: 1, limit: 100 });
  const evidence = response?.items;
  const { hasPermission } = useRBAC();

  const canViewEvidence = hasPermission("evidence:read");
  const recentEvidence = evidence?.slice().sort((a, b) => {
    const da = a.uploaded_at ? new Date(a.uploaded_at).getTime() : 0;
    const db = b.uploaded_at ? new Date(b.uploaded_at).getTime() : 0;
    return db - da;
  }) ?? [];

  if (!canViewEvidence) {
    return null;
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-base">Recent Evidence</CardTitle>
          <CardDescription>
            {isLoading ? "Loading..." : `${recentEvidence.length} item${recentEvidence.length !== 1 ? "s" : ""} uploaded`}
          </CardDescription>
        </div>
        <Button variant="ghost" size="sm">
          View All <ArrowRight className="h-3 w-3 ml-1" />
        </Button>
      </CardHeader>
      <CardContent>
        {isError ? (
          <div className="flex flex-col items-center justify-center py-6">
            <AlertTriangle className="h-6 w-6 text-destructive mb-2" />
            <p className="text-sm text-muted-foreground mb-2">
              {error ? getErrorMessage(error) : "Failed to load evidence"}
            </p>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          </div>
        ) : isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <EvidenceSkeleton key={i} />
            ))}
          </div>
        ) : recentEvidence.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <FileText className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">No evidence uploaded yet</p>
            <p className="text-xs text-muted-foreground mt-1">
              Upload evidence to begin analysis
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {recentEvidence.slice(0, 5).map((e) => (
              <div
                key={e.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center space-x-3 min-w-0">
                  <div className="bg-secondary/50 p-2 rounded shrink-0">
                    <FileText className="h-4 w-4 text-secondary-foreground" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{e.filename}</p>
                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                      <span>{mimeToType(e.mime_type)}</span>
                      <span className="text-muted-foreground/50">|</span>
                      <span>{e.size ? `${(e.size / 1024).toFixed(1)} KB` : "Unknown size"}</span>
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0 ml-2">
                  {e.case_id && (
                    <Badge variant="outline" className="text-xs">
                      {e.case_id.slice(0, 8)}
                    </Badge>
                  )}
                  {e.uploaded_at && (
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(e.uploaded_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
