"use client";

import { memo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Shield,
  Scale,
  Lock,
  Clock,
  AlertTriangle,
  FileCheck,
  Download,
  Activity,
  Briefcase,
  FileX,
} from "lucide-react";
import { useLegalHolds, useRetentionPolicies, useComplianceReportsList } from "../hooks/useCompliance";

interface KPICardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color?: string;
}

function KPICard({ label, value, icon, color = "text-muted-foreground" }: KPICardProps) {
  return (
    <div className="p-3 border rounded-lg space-y-1">
      <div className="flex items-center gap-1.5">
        <span className={color}>{icon}</span>
        <span className="text-[10px] text-muted-foreground">{label}</span>
      </div>
      <div className="text-xl font-bold">{value}</div>
    </div>
  );
}

export const ComplianceKPI = memo(function ComplianceKPI() {
  const { data: holdsData, isLoading: holdsLoading } = useLegalHolds();
  const { data: policiesData, isLoading: policiesLoading } = useRetentionPolicies();
  const { data: reportsData, isLoading: reportsLoading } = useComplianceReportsList();

  const isLoading = holdsLoading || policiesLoading || reportsLoading;

  if (isLoading) {
    return (
      <div className="grid grid-cols-3 lg:grid-cols-5 gap-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="p-3 border rounded-lg space-y-2">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-6 w-10" />
          </div>
        ))}
      </div>
    );
  }

  const activeHolds = (holdsData?.holds?.filter((h) => h.status === "active") ?? []).length;
  const totalPolicies = policiesData?.total ?? 0;
  const totalReports = reportsData?.total ?? 0;

  return (
    <div className="grid grid-cols-3 lg:grid-cols-5 gap-3">
      <KPICard
        label="Active Legal Holds"
        value={activeHolds}
        icon={<Lock className="h-3.5 w-3.5" />}
        color="text-amber-500"
      />
      <KPICard
        label="Retention Policies"
        value={totalPolicies}
        icon={<FileCheck className="h-3.5 w-3.5" />}
        color="text-blue-500"
      />
      <KPICard
        label="Compliance Reports"
        value={totalReports}
        icon={<Shield className="h-3.5 w-3.5" />}
        color="text-emerald-500"
      />
      <KPICard
        label="Total Holds"
        value={holdsData?.total ?? 0}
        icon={<Briefcase className="h-3.5 w-3.5" />}
        color="text-violet-500"
      />
      <KPICard
        label="GDPR Requests"
        value={0}
        icon={<Scale className="h-3.5 w-3.5" />}
        color="text-orange-500"
      />
    </div>
  );
});
