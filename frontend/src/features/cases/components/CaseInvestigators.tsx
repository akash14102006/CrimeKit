"use client";

import { User } from "lucide-react";
import type { CaseOut } from "@/types/case";

interface CaseInvestigatorsProps {
  caseItem: CaseOut;
}

export function CaseInvestigators({ caseItem }: CaseInvestigatorsProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3 rounded-lg border p-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10">
          <User className="h-4 w-4 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium">Case Creator</p>
          <p className="text-xs text-muted-foreground truncate">
            {caseItem.created_by ?? "Unknown"}
          </p>
        </div>
      </div>
      <p className="text-xs text-muted-foreground">
        Additional investigator assignment is managed through the workspace.
      </p>
    </div>
  );
}
