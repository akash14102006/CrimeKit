"use client";

import { AuthGuard } from "@/components/shared/AuthGuard";
import { Breadcrumbs } from "./Breadcrumbs";
import { CaseStats } from "./CaseStats";
import { CaseList } from "./CaseList";
import { useCases } from "@/hooks/queries/useCases";

export function CaseListPage() {
  const { data, isLoading } = useCases({ page: 1, limit: 100 });
  const cases = data?.items;

  return (
    <AuthGuard allowedRoles={["admin", "investigator", "demo_evaluator", "jury_evaluator"]}>

      <div className="space-y-6">
        <Breadcrumbs items={[{ label: "Cases" }]} />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Case Management
          </h1>
          <p className="text-muted-foreground">
            Manage and track forensic investigations.
          </p>
        </div>
        <CaseStats cases={cases} isLoading={isLoading} />
        <CaseList />
      </div>
    </AuthGuard>
  );
}
