"use client";

import { useMemo } from "react";
import { FileText, AlertCircle, Clock, CheckCircle2 } from "lucide-react";
import type { CaseOut } from "@/types/case";
import type { LucideIcon } from "lucide-react";

interface CaseStatsProps {
  cases: CaseOut[] | undefined;
  isLoading: boolean;
}

interface StatItem {
  title: string;
  value: number;
  icon: LucideIcon;
  description: string;
  trend: string;
  trendPositive: boolean;
  iconBg: string;
  iconColor: string;
}

export function CaseStats({ cases, isLoading }: CaseStatsProps) {
  const total = cases?.length ?? 0;
  const openCount = (cases?.filter((c) => c.status === "open") ?? []).length;
  const reviewCount = (cases?.filter((c) => c.status === "review") ?? []).length;
  const closedCount = (cases?.filter((c) => c.status === "closed") ?? []).length;

  const stats: StatItem[] = useMemo(
    () => [
      {
        title: "TOTAL CASES",
        value: total,
        icon: FileText,
        description: "All registered investigation files",
        trend: "+14.2% this month",
        trendPositive: true,
        iconBg: "bg-blue-100",
        iconColor: "text-blue-600",
      },
      {
        title: "OPEN CASES",
        value: openCount,
        icon: AlertCircle,
        description: "Active forensic investigations",
        trend: "Requires immediate action",
        trendPositive: false,
        iconBg: "bg-red-100",
        iconColor: "text-red-500",
      },
      {
        title: "IN REVIEW",
        value: reviewCount,
        icon: Clock,
        description: "Pending supervisor approval",
        trend: "3 awaiting triage",
        trendPositive: true,
        iconBg: "bg-amber-100",
        iconColor: "text-amber-500",
      },
      {
        title: "CLOSED",
        value: closedCount,
        icon: CheckCircle2,
        description: "Archived & resolved cases",
        trend: "+98.4% resolution rate",
        trendPositive: true,
        iconBg: "bg-emerald-100",
        iconColor: "text-emerald-500",
      },
    ],
    [total, openCount, reviewCount, closedCount]
  );

  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => {
        const IconComponent = stat.icon;

        return (
          <div
            key={stat.title}
            className="group relative p-5 rounded-xl bg-white dark:bg-card border border-gray-200 dark:border-white/10 transition-all duration-200 hover:shadow-md"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className={`p-2.5 rounded-full ${stat.iconBg}`}>
                <IconComponent className={`h-5 w-5 ${stat.iconColor}`} />
              </div>
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-white/50 block">
                  {stat.title}
                </span>
                <span className="text-[11px] text-gray-400 dark:text-white/40 block leading-tight">
                  {stat.description}
                </span>
              </div>
            </div>

            <div className="flex items-baseline justify-between mt-2">
              <div className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white font-mono">
                {isLoading ? (
                  <span className="animate-pulse text-gray-300 dark:text-white/30">—</span>
                ) : (
                  stat.value
                )}
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-gray-100 dark:border-white/5 flex items-center gap-1.5 text-xs">
              {stat.trendPositive ? (
                <span className="text-emerald-500">↗</span>
              ) : (
                <span className="text-red-500">↗</span>
              )}
              <span className={stat.trendPositive ? "text-emerald-500 font-medium" : "text-red-500 font-medium"}>
                {stat.trend}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
