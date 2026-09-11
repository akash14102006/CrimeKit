"use client";

import { memo, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  History,
  RefreshCw,
  Eye,
  Download,
  Trash2,
  FileText,
  Scale,
  Clock,
  User,
} from "lucide-react";
import { useCaseReports, useDeleteReport } from "../hooks/useReports";
import { useReportStore } from "../store/reportStore";
import { toast } from "@/components/ui/toast";
import type { Report } from "@/types/report";

const STATUS_CONFIG: Record<string, { color: string }> = {
  generated: { color: "bg-emerald-100 text-emerald-700" },
  pending: { color: "bg-amber-100 text-amber-700" },
  generating: { color: "bg-blue-100 text-blue-700" },
  failed: { color: "bg-red-100 text-red-700" },
  queued: { color: "bg-purple-100 text-purple-700" },
};

function ReportRow({ report }: { report: Report }) {
  const { setSelectedReport } = useReportStore();
  const deleteReport = useDeleteReport();
  const statusConfig = STATUS_CONFIG[report.status] || STATUS_CONFIG.generated;

  const handleDelete = useCallback(async () => {
    try {
      await deleteReport.mutateAsync(report.id);
      toast.add({
        title: "Report Deleted",
        description: `"${report.title}" has been deleted.`,
        type: "success",
      });
    } catch {
      toast.add({
        title: "Delete Failed",
        description: "Could not delete the report.",
        type: "error",
      });
    }
  }, [deleteReport, report]);

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/30 transition-colors">
      <div className="p-2 rounded-md bg-primary/10 shrink-0">
        <FileText className="h-4 w-4 text-primary" />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h4 className="text-xs font-medium truncate">{report.title}</h4>
          <Badge className={`text-[8px] ${statusConfig.color}`}>
            {report.status}
          </Badge>
        </div>
        <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
          <span className="flex items-center gap-0.5">
            <Scale className="h-2.5 w-2.5" />
            {report.report_type}
          </span>
          <span className="flex items-center gap-0.5">
            <User className="h-2.5 w-2.5" />
            {report.created_by}
          </span>
          <span className="flex items-center gap-0.5">
            <Clock className="h-2.5 w-2.5" />
            {new Date(report.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-1 shrink-0">
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0"
          onClick={() => setSelectedReport(report)}
        >
          <Eye className="h-3 w-3" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0"
          onClick={() => {
            navigator.clipboard.writeText(report.content_markdown);
            toast.add({ title: "Copied", description: "Report content copied.", type: "success" });
          }}
        >
          <Download className="h-3 w-3" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0 text-destructive"
          onClick={handleDelete}
          disabled={deleteReport.isPending}
        >
          <Trash2 className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}

function ReportHistorySkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-3 border rounded-lg">
          <Skeleton className="h-8 w-8 rounded" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-3 w-32" />
            <Skeleton className="h-2 w-48" />
          </div>
          <Skeleton className="h-5 w-16" />
        </div>
      ))}
    </div>
  );
}

export const ReportHistory = memo(function ReportHistory({
  caseId,
}: {
  caseId?: string;
}) {
  const { data: reports, isLoading, refetch } = useCaseReports(caseId || null);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <History className="h-4 w-4" />
          Report History
          {reports && reports.length > 0 && (
            <Badge variant="secondary" className="text-[10px]">
              {reports.length}
            </Badge>
          )}
        </CardTitle>
        <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => refetch()}>
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <ReportHistorySkeleton />
        ) : !reports || reports.length === 0 ? (
          <div className="text-center py-6">
            <FileText className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
            <p className="text-sm font-medium">No Reports</p>
            <p className="text-xs text-muted-foreground">
              Generate a report from a template to get started.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {reports.map((report) => (
              <ReportRow key={report.id} report={report} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
});
