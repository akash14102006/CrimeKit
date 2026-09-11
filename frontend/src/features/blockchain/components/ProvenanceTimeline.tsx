"use client";

import {
  Upload,
  Cpu,
  FileOutput,
  Link2,
  Clock,
  Loader2,
  Hash,
  Wrench,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useProvenance } from "../hooks/useBlockchain";
import { cn } from "@/lib/utils";

interface Props {
  evidenceId: string;
}

const stepIcons: Record<string, React.ElementType> = {
  upload: Upload,
  upload_hash: Upload,
  processing: Cpu,
  processed: Cpu,
  artifact: FileOutput,
  artifacts: FileOutput,
  anchor: Link2,
  anchored: Link2,
};

const stepColors: Record<string, string> = {
  upload: "border-blue-500 bg-blue-500/10 text-blue-500",
  upload_hash: "border-blue-500 bg-blue-500/10 text-blue-500",
  processing: "border-amber-500 bg-amber-500/10 text-amber-500",
  processed: "border-amber-500 bg-amber-500/10 text-amber-500",
  artifact: "border-purple-500 bg-purple-500/10 text-purple-500",
  artifacts: "border-purple-500 bg-purple-500/10 text-purple-500",
  anchor: "border-green-500 bg-green-500/10 text-green-500",
  anchored: "border-green-500 bg-green-500/10 text-green-500",
};

const lineColors: Record<string, string> = {
  upload: "bg-blue-500",
  upload_hash: "bg-blue-500",
  processing: "bg-amber-500",
  processed: "bg-amber-500",
  artifact: "bg-purple-500",
  artifacts: "bg-purple-500",
  anchor: "bg-green-500",
  anchored: "bg-green-500",
};

export function ProvenanceTimeline({ evidenceId }: Props) {
  const { data: provenance, isLoading, error } = useProvenance(evidenceId);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Provenance Timeline
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex gap-3">
                <Skeleton className="h-10 w-10 rounded-full shrink-0" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-3 w-48" />
                  <Skeleton className="h-3 w-32" />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <p className="text-sm text-muted-foreground">
              Could not load provenance timeline.
            </p>
          </div>
        ) : provenance && provenance.timeline.length > 0 ? (
          <div className="relative">
            {provenance.timeline.map((entry, index) => {
              const StepIcon = stepIcons[entry.step] || Hash;
              const colorClass = stepColors[entry.step] || "border-muted-foreground bg-muted text-muted-foreground";
              const lineColor = lineColors[entry.step] || "bg-border";
              const isLast = index === provenance.timeline.length - 1;

              return (
                <div key={index} className="flex gap-3 pb-4 relative">
                  {!isLast && (
                    <div
                      className={cn(
                        "absolute left-[19px] top-10 w-0.5 h-[calc(100%-16px)]",
                        lineColor
                      )}
                    />
                  )}
                  <div
                    className={cn(
                      "relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2",
                      colorClass
                    )}
                  >
                    <StepIcon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0 pt-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-medium capitalize">
                        {entry.step.replace(/_/g, " ")}
                      </span>
                      <Badge variant="secondary" className="text-[10px]">
                        {new Date(entry.timestamp).toLocaleString()}
                      </Badge>
                    </div>
                    {entry.hash && (
                      <div className="mt-1 flex items-center gap-1.5">
                        <Hash className="h-3 w-3 text-muted-foreground shrink-0" />
                        <span className="text-xs font-mono text-muted-foreground truncate">
                          {entry.hash.length > 20
                            ? `${entry.hash.slice(0, 10)}...${entry.hash.slice(-8)}`
                            : entry.hash}
                        </span>
                      </div>
                    )}
                    {entry.tool && (
                      <div className="mt-0.5 flex items-center gap-1.5">
                        <Wrench className="h-3 w-3 text-muted-foreground shrink-0" />
                        <span className="text-xs text-muted-foreground">
                          {entry.tool}
                        </span>
                      </div>
                    )}
                    {Object.keys(entry.details).length > 0 && (
                      <div className="mt-1.5 rounded-md bg-muted/50 p-2">
                        {Object.entries(entry.details).map(([key, value]) => (
                          <div key={key} className="flex items-center justify-between gap-2">
                            <span className="text-[11px] text-muted-foreground capitalize">
                              {key.replace(/_/g, " ")}
                            </span>
                            <span className="text-[11px] font-mono text-muted-foreground truncate max-w-[180px]">
                              {typeof value === "string" ? value : JSON.stringify(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Clock className="h-10 w-10 text-muted-foreground/50 mb-2" />
            <p className="text-sm text-muted-foreground">
              No provenance data available for this evidence.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
