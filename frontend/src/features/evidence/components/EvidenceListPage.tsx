"use client";

import { AuthGuard } from "@/components/shared/AuthGuard";
import { EvidenceBreadcrumbs } from "./EvidenceBreadcrumbs";
import { EvidenceStats } from "./EvidenceStats";
import { EvidenceList } from "./EvidenceList";
import { EvidenceUploadDialog } from "./EvidenceUploadDialog";
import { useRBAC } from "@/hooks/useRBAC";

export function EvidenceListPage() {
  const { hasPermission } = useRBAC();
  const canUpload = hasPermission("case:update") || hasPermission("case:create");

  return (
    <AuthGuard allowedRoles={["admin", "investigator", "analyst", "viewer", "demo_evaluator", "jury_evaluator"]}>

      <div className="space-y-6">
        <EvidenceBreadcrumbs items={[{ label: "Evidence" }]} />
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Evidence Library</h1>
            <p className="text-muted-foreground">
              Manage, view, and analyze all digital evidence across cases.
            </p>
          </div>
          {canUpload && <EvidenceUploadDialog />}
        </div>
        <EvidenceStats />
        <EvidenceList />
      </div>
    </AuthGuard>
  );
}
