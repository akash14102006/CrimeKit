"use client";

import { Suspense } from "react";
import { Loader2 } from "lucide-react";
import { AuthGuard } from "@/components/shared/AuthGuard";
import ComplianceContent from "@/features/compliance/components/CompliancePage";

function ComplianceFallback() {
  return (
    <div className="flex h-[400px] items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );
}

export default function CompliancePageRoute() {
  return (
    <AuthGuard allowedRoles={["admin", "investigator", "analyst", "compliance_officer"]}>
      <Suspense fallback={<ComplianceFallback />}>
        <ComplianceContent />
      </Suspense>
    </AuthGuard>
  );
}
