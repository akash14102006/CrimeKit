"use client";

import Link from "next/link";
import {
  ExternalLink,
  FileText,
  Upload,
  BarChart3,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRBAC } from "@/hooks/useRBAC";
import { EvidenceUploadDialog } from "@/features/evidence/components/EvidenceUploadDialog";

interface CaseQuickActionsProps {
  caseId: string;
}

export function CaseQuickActions({ caseId }: CaseQuickActionsProps) {
  const { hasPermission } = useRBAC();

  return (
    <div className="flex flex-wrap gap-2">
      <Link href={`/workspace/${caseId}`}>
        <Button variant="outline" size="sm" className="gap-1.5">
          <ExternalLink className="h-3.5 w-3.5" />
          Open Workspace
        </Button>
      </Link>
      {hasPermission("evidence:upload") && (
        <EvidenceUploadDialog initialCaseId={caseId} />
      )}
      <Link href={`/timeline`}>
        <Button variant="outline" size="sm" className="gap-1.5">
          <BarChart3 className="h-3.5 w-3.5" />
          Timeline
        </Button>
      </Link>
      <Link href={`/reports/${caseId}`}>
        <Button variant="outline" size="sm" className="gap-1.5">
          <FileText className="h-3.5 w-3.5" />
          Reports
        </Button>
      </Link>
    </div>
  );
}
