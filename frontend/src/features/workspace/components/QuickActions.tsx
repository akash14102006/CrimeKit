"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Upload,
  FileSearch,
  Printer,
  Search,
} from "lucide-react";

interface Props {
  caseId: string;
}

export function QuickActions({ caseId }: Props) {
  const router = useRouter();

  const actions = [
    {
      label: "Upload Evidence",
      icon: Upload,
      onClick: () => router.push(`/cases/${caseId}?upload=true`),
      variant: "default" as const,
    },
    {
      label: "Search Evidence",
      icon: Search,
      onClick: () => router.push(`/evidence?case=${caseId}`),
      variant: "outline" as const,
    },
    {
      label: "Court Report",
      icon: Printer,
      onClick: () => router.push(`/cases/${caseId}/court-report`),
      variant: "outline" as const,
    },
    {
      label: "Case Details",
      icon: FileSearch,
      onClick: () => router.push(`/cases/${caseId}`),
      variant: "ghost" as const,
    },
  ];

  return (
    <div className="flex flex-wrap gap-2 p-3">
      {actions.map((action) => {
        const Icon = action.icon;
        return (
          <Button
            key={action.label}
            variant={action.variant}
            size="sm"
            className="h-8 gap-1.5"
            onClick={action.onClick}
          >
            <Icon className="h-3.5 w-3.5" />
            {action.label}
          </Button>
        );
      })}
    </div>
  );
}
