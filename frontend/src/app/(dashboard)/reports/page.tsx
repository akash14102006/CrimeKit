"use client";

import { Suspense } from "react";
import { Loader2 } from "lucide-react";
import { AuthGuard } from "@/components/shared/AuthGuard";
import ReportsContent from "@/features/reports/components/ReportsPage";

function ReportsFallback() {
  return (
    <div className="flex h-[400px] items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );
}

export default function ReportsPageRoute() {
  return (
    <AuthGuard allowedRoles={["admin", "investigator", "analyst", "evidence_officer", "compliance_officer"]}>
      <Suspense fallback={<ReportsFallback />}>
        <ReportsContent />
      </Suspense>
    </AuthGuard>
  );
}
