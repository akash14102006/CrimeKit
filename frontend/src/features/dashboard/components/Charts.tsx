"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useCasesSummary, useEvidenceSummary, useMetrics } from "@/hooks/queries/useDashboard";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const PIE_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

function ChartSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-48 w-full rounded" />
    </div>
  );
}

function ChartError({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      <AlertTriangle className="h-6 w-6 text-destructive mb-2" />
      <p className="text-sm text-muted-foreground mb-2">Failed to load chart data</p>
      <Button variant="outline" size="sm" onClick={onRetry}>
        <RefreshCw className="h-3 w-3 mr-1" />
        Retry
      </Button>
    </div>
  );
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number }>; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-background border rounded-lg shadow-lg p-2 text-xs">
      <p className="font-medium">{label}</p>
      {payload.map((entry, i) => (
        <p key={i} className="text-muted-foreground">
          {entry.name}: {entry.value}
        </p>
      ))}
    </div>
  );
}

export function CaseStatusChart() {
  const { data: summary, isLoading, isError, refetch } = useCasesSummary();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Case Distribution</CardTitle>
        <CardDescription>Cases by status</CardDescription>
      </CardHeader>
      <CardContent>
        {isError ? (
          <ChartError onRetry={() => refetch()} />
        ) : isLoading || !summary ? (
          <ChartSkeleton />
        ) : summary.total === 0 ? (
          <div className="flex items-center justify-center h-48 text-sm text-muted-foreground">
            No cases to display
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={summary.byStatus.filter((s) => s.value > 0)}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {summary.byStatus
                  .filter((s) => s.value > 0)
                  .map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend
                formatter={(value: string) => (
                  <span className="text-xs">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

export function EvidenceTypeChart() {
  const { data: summary, isLoading, isError, refetch } = useEvidenceSummary();

  const barData = summary
    ? Object.entries(summary.byType).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        count: value,
      }))
    : [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Evidence by Type</CardTitle>
        <CardDescription>Distribution of evidence types</CardDescription>
      </CardHeader>
      <CardContent>
        {isError ? (
          <ChartError onRetry={() => refetch()} />
        ) : isLoading || !summary ? (
          <ChartSkeleton />
        ) : summary.total === 0 ? (
          <div className="flex items-center justify-center h-48 text-sm text-muted-foreground">
            No evidence to display
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

export function MetricsChart() {
  const { data: metrics, isLoading, isError, refetch } = useMetrics();

  const jobData = metrics
    ? Object.entries(metrics.forensic_jobs).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        count: value,
      }))
    : [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Processing Metrics</CardTitle>
        <CardDescription>Forensic job distribution</CardDescription>
      </CardHeader>
      <CardContent>
        {isError ? (
          <ChartError onRetry={() => refetch()} />
        ) : isLoading || !metrics ? (
          <ChartSkeleton />
        ) : jobData.length === 0 ? (
          <div className="flex items-center justify-center h-48 text-sm text-muted-foreground">
            No metrics available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={jobData}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
