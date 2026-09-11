"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatBytes } from "@/lib/utils";
import type { Evidence, ForensicImageMetadata } from "@/types/evidence";
import { OpenDiskAnalyzerAction } from "./OpenDiskAnalyzerAction";

interface Props {
  evidence: Evidence | undefined;
  isLoading: boolean;
}

export function EvidenceMetadataCard({ evidence, isLoading }: Props) {
  const meta = evidence?.metadata as Record<string, string> | null | undefined;
  const forensic = evidence?.metadata as ForensicImageMetadata | null | undefined;
  const isForensicImage = forensic?.evidence_type === "forensic_disk_image" ||
    /\.(e01|ex01|ewf)$/i.test(evidence?.filename ?? "");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Metadata</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex justify-between">
                <Skeleton className="h-4 w-[100px]" />
                <Skeleton className="h-4 w-[150px]" />
              </div>
            ))}
          </div>
        ) : (
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Filename</dt>
              <dd className="font-medium text-right max-w-[200px] truncate">{evidence?.filename}</dd>
            </div>
            {isForensicImage && (
              <div className="space-y-3 rounded-md border border-amber-500/30 bg-amber-500/5 p-3">
                <div className="flex justify-between"><dt className="text-muted-foreground">Type</dt><dd className="font-medium">E01 Forensic Disk Image</dd></div>
                <div className="flex justify-between"><dt className="text-muted-foreground">Processor</dt><dd className="font-medium">{forensic?.processor ?? "TSK"}</dd></div>
                <div className="flex justify-between"><dt className="text-muted-foreground">Status</dt><dd className="font-medium">{forensic?.capability === "unsupported" ? "Unavailable" : "Ready for Analysis"}</dd></div>
                {forensic?.capability === "unsupported" && forensic.capability_reason && <p className="text-xs text-destructive">{forensic.capability_reason}</p>}
                {evidence && <OpenDiskAnalyzerAction evidence={evidence} />}
              </div>
            )}
            <div className="flex justify-between">
              <dt className="text-muted-foreground">MIME Type</dt>
              <dd className="font-medium">{evidence?.mime_type ?? "Unknown"}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Size</dt>
              <dd className="font-medium">{formatBytes(evidence?.size ?? 0)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Case ID</dt>
              <dd className="font-medium font-mono text-xs">
                {evidence?.case_id ? evidence.case_id.split("-")[0] + "..." : "Unassigned"}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Uploaded By</dt>
              <dd className="font-medium font-mono text-xs">
                {evidence?.uploaded_by ? evidence.uploaded_by.split("-")[0] + "..." : "Unknown"}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Uploaded At</dt>
              <dd className="font-medium">
                {evidence?.uploaded_at
                  ? new Date(evidence.uploaded_at).toLocaleString()
                  : "Unknown"}
              </dd>
            </div>
            {meta?.created_at && (
              <div className="flex justify-between">
                <dt className="text-muted-foreground">File Created</dt>
                <dd className="font-medium">{meta.created_at}</dd>
              </div>
            )}
            {meta?.modified_at && (
              <div className="flex justify-between">
                <dt className="text-muted-foreground">File Modified</dt>
                <dd className="font-medium">{meta.modified_at}</dd>
              </div>
            )}
          </dl>
        )}
      </CardContent>
    </Card>
  );
}
