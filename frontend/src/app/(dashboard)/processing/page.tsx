"use client";

import { Suspense } from "react";
import { Loader2 } from "lucide-react";
import { AuthGuard } from "@/components/shared/AuthGuard";
import ProcessingContent from "@/features/processing/components/ProcessingPage";

function ProcessingFallback() {
  return (
    <div className="flex h-[400px] items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );
}

export default function ProcessingPageRoute() {
  return (
    <AuthGuard allowedRoles={["admin", "investigator", "analyst", "demo_evaluator", "jury_evaluator"]}>

      <Suspense fallback={<ProcessingFallback />}>
        <ProcessingContent />
      </Suspense>
    </AuthGuard>
  );
}
