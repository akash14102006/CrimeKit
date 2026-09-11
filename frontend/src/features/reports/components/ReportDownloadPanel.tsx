"use client";

import { memo, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Download,
  FileText,
  File,
  FileJson,
  Archive,
  Loader2,
} from "lucide-react";
import { useExportReport } from "../hooks/useReports";
import { useReportStore } from "../store/reportStore";
import { toast } from "@/components/ui/toast";

const FORMAT_OPTIONS = [
  { format: "pdf" as const, label: "PDF", icon: <FileText className="h-3.5 w-3.5" />, color: "text-red-600" },
  { format: "docx" as const, label: "DOCX", icon: <File className="h-3.5 w-3.5" />, color: "text-blue-600" },
  { format: "json" as const, label: "JSON", icon: <FileJson className="h-3.5 w-3.5" />, color: "text-amber-600" },
  { format: "zip" as const, label: "ZIP Package", icon: <Archive className="h-3.5 w-3.5" />, color: "text-purple-600" },
];

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export const ReportDownloadPanel = memo(function ReportDownloadPanel() {
  const { selectedReport } = useReportStore();
  const exportReport = useExportReport();

  const handleDownload = useCallback(
    async (format: "pdf" | "docx" | "json" | "zip") => {
      if (!selectedReport) return;

      try {
        const blob = await exportReport.mutateAsync({
          reportId: selectedReport.id,
          format,
        });
        const ext = format === "zip" ? "zip" : format;
        downloadBlob(blob, `${selectedReport.title}.${ext}`);
        toast.add({
          title: "Download Complete",
          description: `${format.toUpperCase()} report downloaded.`,
          type: "success",
        });
      } catch {
        toast.add({
          title: "Download Failed",
          description: `Could not download ${format.toUpperCase()} report.`,
          type: "error",
        });
      }
    },
    [selectedReport, exportReport],
  );

  if (!selectedReport) {
    return (
      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export Report
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <Download className="h-6 w-6 mx-auto text-muted-foreground/30 mb-2" />
            <p className="text-xs text-muted-foreground">
              Select a report to export
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Download className="h-4 w-4" />
          Export Report
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="p-2 rounded bg-muted/50">
            <p className="text-xs font-medium truncate">{selectedReport.title}</p>
            <p className="text-[10px] text-muted-foreground">{selectedReport.report_type}</p>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {FORMAT_OPTIONS.map((opt) => (
              <Button
                key={opt.format}
                variant="outline"
                size="sm"
                className="h-9 gap-2"
                onClick={() => handleDownload(opt.format)}
                disabled={exportReport.isPending}
              >
                {exportReport.isPending ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <span className={opt.color}>{opt.icon}</span>
                )}
                {opt.label}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
});
