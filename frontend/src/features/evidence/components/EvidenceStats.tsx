"use client";

import { FileText, HardDrive, CheckCircle2, AlertTriangle } from "lucide-react";
import { MetricCard } from "@/components/ui/metric-card";
import { useAllEvidence } from "@/hooks/queries/useEvidence";
import { formatBytes } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

export function EvidenceStats() {
  const { data, isLoading } = useAllEvidence({ page: 1, limit: 100 });
  const evidence = data?.items;

  const total = data?.total ?? 0;
  const totalSize = evidence?.reduce((sum, e) => sum + (e.size ?? 0), 0) ?? 0;
  const imageCount = (evidence?.filter((e) => e.mime_type?.startsWith("image/")) ?? []).length;
  const docCount = (evidence?.filter((e) => e.mime_type?.includes("pdf") || e.mime_type?.includes("document")) ?? []).length;

  const stats: Array<{
    title: string;
    value: string | number;
    icon: LucideIcon;
    description: string;
    tone?: "default" | "success" | "warning" | "destructive";
  }> = [
    { title: "Total Items", value: isLoading ? "—" : total, icon: FileText, description: "Evidence artifacts" },
    { title: "Total Size", value: isLoading ? "—" : formatBytes(totalSize), icon: HardDrive, description: "Storage used" },
    { title: "Images", value: isLoading ? "—" : imageCount, icon: CheckCircle2, description: "Image evidence", tone: "success" },
    { title: "Documents", value: isLoading ? "—" : docCount, icon: AlertTriangle, description: "Document evidence", tone: "warning" },
  ];

  return (
    <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <MetricCard
          key={stat.title}
          title={stat.title}
          value={stat.value}
          icon={stat.icon}
          description={stat.description}
          tone={stat.tone}
        />
      ))}
    </div>
  );
}
