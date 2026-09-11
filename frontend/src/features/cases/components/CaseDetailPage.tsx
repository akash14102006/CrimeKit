"use client";

import Link from "next/link";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { ErrorState } from "@/components/shared/ErrorState";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/ui/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useCase } from "@/hooks/queries/useCases";
import { useRBAC } from "@/hooks/useRBAC";
import { Breadcrumbs } from "./Breadcrumbs";
import { EditCaseDialog } from "./EditCaseDialog";
import { DeleteCaseDialog } from "./DeleteCaseDialog";
import { CaseTimelinePreview } from "./CaseTimelinePreview";
import { CaseEvidenceSummary } from "./CaseEvidenceSummary";
import { CaseInvestigators } from "./CaseInvestigators";
import { CaseQuickActions } from "./CaseQuickActions";

interface CaseDetailPageProps {
  caseId: string;
}

export function CaseDetailPage({ caseId }: CaseDetailPageProps) {
  const { data: caseItem, isLoading, isError, refetch } = useCase(caseId);
  const { hasPermission } = useRBAC();

  if (isError) {
    return (
      <AuthGuard allowedRoles={["admin", "investigator"]}>
        <div className="space-y-6">
          <Breadcrumbs
            items={[
              { label: "Cases", href: "/cases" },
              { label: "Not Found" },
            ]}
          />
          <ErrorState
            title="Case not found"
            description="The case you are looking for does not exist or you do not have access."
            onRetry={() => refetch()}
          />
        </div>
      </AuthGuard>
    );
  }

  if (isLoading || !caseItem) {
    return (
      <AuthGuard allowedRoles={["admin", "investigator"]}>
        <div className="space-y-6">
          <Skeleton className="h-5 w-[200px]" />
          <Skeleton className="h-8 w-[300px]" />
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2 space-y-4">
              <Skeleton className="h-[200px] w-full rounded-xl" />
              <Skeleton className="h-[200px] w-full rounded-xl" />
            </div>
            <div className="space-y-4">
              <Skeleton className="h-[150px] w-full rounded-xl" />
              <Skeleton className="h-[150px] w-full rounded-xl" />
            </div>
          </div>
        </div>
      </AuthGuard>
    );
  }

  const canWrite = hasPermission("case:update");
  const canDelete = hasPermission("case:delete");

  return (
    <AuthGuard allowedRoles={["admin", "investigator"]}>
      <div className="space-y-6">
        <Breadcrumbs
          items={[
            { label: "Cases", href: "/cases" },
            { label: caseItem?.title ?? "Loading..." },
          ]}
        />

        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {caseItem?.title}
            </h1>
            <div className="mt-2 flex items-center gap-3">
              <StatusBadge status={caseItem?.status ?? "open"} />
              <span className="text-sm text-muted-foreground">
                Created{" "}
                {caseItem?.created_at
                  ? new Date(caseItem.created_at).toLocaleDateString()
                  : "—"}
              </span>
              <span className="text-sm text-muted-foreground font-mono">
                ID: {caseItem?.id?.split("-")[0]}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {canWrite && caseItem && <EditCaseDialog caseItem={caseItem} />}
            {canDelete && caseItem && <DeleteCaseDialog caseItem={caseItem} />}
          </div>
        </div>

        <CaseQuickActions caseId={caseId} />

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Description</CardTitle>
              </CardHeader>
              <CardContent>
                {caseItem?.description ? (
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {caseItem.description}
                  </p>
                ) : (
                  <p className="text-sm text-muted-foreground italic">
                    No description provided.
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <CaseTimelinePreview caseId={caseId} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Related Evidence</CardTitle>
              </CardHeader>
              <CardContent>
                <CaseEvidenceSummary caseId={caseId} />
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Investigators</CardTitle>
              </CardHeader>
              <CardContent>
                {caseItem && <CaseInvestigators caseItem={caseItem} />}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Case Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Status</span>
                  <StatusBadge status={caseItem?.status ?? "open"} />
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Created</span>
                  <span>
                    {caseItem?.created_at
                      ? new Date(caseItem.created_at).toLocaleDateString()
                      : "—"}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Creator</span>
                  <span className="font-mono text-xs truncate max-w-[120px]">
                    {caseItem?.created_by ?? "—"}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Case ID</span>
                  <Link
                    href={`/workspace/${caseItem?.id}`}
                    className="text-primary hover:underline text-xs font-mono"
                  >
                    {caseItem?.id?.split("-")[0]}
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AuthGuard>
  );
}
