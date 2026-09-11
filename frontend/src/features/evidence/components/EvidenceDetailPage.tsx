"use client";

import { useParams } from "next/navigation";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { EvidenceBreadcrumbs } from "./EvidenceBreadcrumbs";
import { EvidenceMetadataCard } from "./EvidenceMetadataCard";
import { EvidenceHashCard } from "./EvidenceHashCard";
import { EvidenceIntegrityCard } from "./EvidenceIntegrityCard";
import { EvidenceCustodyCard } from "./EvidenceCustodyCard";
import { EvidenceProcessingCard } from "./EvidenceProcessingCard";
import { EvidencePreviewCard } from "./EvidencePreviewCard";
import { EvidenceForensicsCard } from "./EvidenceForensicsCard";
import { EvidenceActions } from "./EvidenceActions";
import { Skeleton } from "@/components/ui/skeleton";
import { useEvidence } from "@/hooks/queries/useEvidence";
import { ErrorState } from "@/components/shared/ErrorState";

export function EvidenceDetailPage() {
  const params = useParams();
  const evidenceId = params.evidenceId as string;
  const { data: evidence, isLoading, isError, refetch } = useEvidence(evidenceId);

  if (isError) {
    return (
      <AuthGuard allowedRoles={["admin", "investigator", "analyst", "viewer"]}>
        <div className="space-y-6">
          <EvidenceBreadcrumbs items={[{ label: "Evidence", href: "/evidence" }, { label: "Not Found" }]} />
          <ErrorState
            title="Evidence not found"
            description="The evidence item could not be loaded."
            onRetry={() => refetch()}
          />
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard allowedRoles={["admin", "investigator", "analyst", "viewer"]}>
      <div className="space-y-6">
        <EvidenceBreadcrumbs
          items={[
            { label: "Evidence", href: "/evidence" },
            { label: evidence?.filename ?? (isLoading ? "Loading..." : "Unknown") },
          ]}
        />

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {isLoading ? <Skeleton className="h-8 w-[300px]" /> : evidence?.filename ?? "Evidence"}
            </h1>
            <div className="text-muted-foreground text-sm">
              {isLoading ? <Skeleton className="h-4 w-[200px] mt-1" /> : `ID: ${evidence?.id}`}
            </div>
          </div>
          {evidence && <EvidenceActions evidence={evidence} />}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <EvidenceMetadataCard evidence={evidence} isLoading={isLoading} />
          <EvidenceHashCard evidence={evidence} isLoading={isLoading} />
          <EvidenceIntegrityCard evidenceId={evidenceId} />
          <EvidencePreviewCard evidence={evidence} isLoading={isLoading} />
        </div>

        <EvidenceForensicsCard evidenceId={evidenceId} />
        <EvidenceProcessingCard evidenceId={evidenceId} />
        <EvidenceCustodyCard evidenceId={evidenceId} />
      </div>
    </AuthGuard>
  );
}
