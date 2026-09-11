"use client";

import dynamic from "next/dynamic";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { KPIRow } from "@/features/dashboard/components/KPIRow";
import { ActiveCases } from "@/features/dashboard/components/ActiveCases";
import { RecentEvidence } from "@/features/dashboard/components/RecentEvidence";
import { AIAlerts } from "@/features/dashboard/components/AIAlerts";
import { ProcessingQueue } from "@/features/dashboard/components/ProcessingQueue";
import { SystemHealth } from "@/features/dashboard/components/SystemHealth";
import { ActivityFeed } from "@/features/dashboard/components/ActivityFeed";
import { QuickActions } from "@/features/dashboard/components/QuickActions";
import { Skeleton } from "@/components/ui/skeleton";
import { Suspense } from "react";

const CaseStatusChart = dynamic(
  () => import("@/features/dashboard/components/Charts").then((m) => m.CaseStatusChart),
  { ssr: false },
);
const EvidenceTypeChart = dynamic(
  () => import("@/features/dashboard/components/Charts").then((m) => m.EvidenceTypeChart),
  { ssr: false },
);
const MetricsChart = dynamic(
  () => import("@/features/dashboard/components/Charts").then((m) => m.MetricsChart),
  { ssr: false },
);

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

export default function DashboardPage() {
  const { user } = useCurrentUser();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          {greeting()}, {user?.name ?? "Investigator"}
        </h1>
        <p className="text-muted-foreground">
          {user?.organization
            ? `${user.organization} — Investigation Command Center`
            : "CrimeKit Enterprise Investigation Command Center"}
        </p>
      </div>

      {/* Quick Actions */}
      <QuickActions />

      {/* Executive KPI Row */}
      <section aria-label="Key performance indicators">
        <KPIRow />
      </section>

      {/* Operational Metrics - Charts */}
      <section aria-label="Analytics and charts">
        <Suspense
          fallback={
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[0, 1, 2].map((i) => (
                <div key={i} className="space-y-4">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-48 w-full rounded" />
                </div>
              ))}
            </div>
          }
        >
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <CaseStatusChart />
            <EvidenceTypeChart />
            <MetricsChart />
          </div>
        </Suspense>
      </section>

      {/* Investigation Overview */}
      <section aria-label="Investigation overview">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
          <div className="lg:col-span-4">
            <ActiveCases />
          </div>
          <div className="lg:col-span-3">
            <RecentEvidence />
          </div>
        </div>
      </section>

      {/* Processing & AI Intelligence */}
      <section aria-label="Processing and AI intelligence">
        <div className="grid gap-6 md:grid-cols-2">
          <ProcessingQueue />
          <AIAlerts />
        </div>
      </section>

      {/* System Health & Activity Feed */}
      <section aria-label="System health and activity">
        <div className="grid gap-6 md:grid-cols-2">
          <SystemHealth />
          <ActivityFeed />
        </div>
      </section>
    </div>
  );
}
