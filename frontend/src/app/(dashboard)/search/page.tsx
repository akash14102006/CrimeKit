"use client";

import { Suspense } from "react";
import { Loader2 } from "lucide-react";
import { AuthGuard } from "@/components/shared/AuthGuard";
import SearchContent from "@/features/search/components/SearchPage";

function SearchFallback() {
  return (
    <div className="flex h-[400px] items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );
}

export default function SearchPage() {
  return (
    <AuthGuard
      allowedRoles={["admin", "investigator", "analyst", "evidence_officer", "compliance_officer", "auditor", "viewer"]}
    >
      <Suspense fallback={<SearchFallback />}>
        <SearchContent />
      </Suspense>
    </AuthGuard>
  );
}
