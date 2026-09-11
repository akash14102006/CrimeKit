"use client";

import { memo, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Loader2,
  FileText,
  Scale,
  Link,
  Shield,
  FileBarChart,
  CheckSquare,
  Search,
  CalendarClock,
  Workflow,
  Cpu,
  AlertTriangle,
} from "lucide-react";
import { useReportStore } from "../store/reportStore";
import { useGenerateReport, useGenerateComplianceReport } from "../hooks/useReports";
import { REPORT_TEMPLATES } from "@/types/report";
import { toast } from "@/components/ui/toast";
import type { ReportType } from "@/types/report";
import type { ComplianceReportType } from "@/types/compliance";

const ICON_MAP: Record<string, React.ReactNode> = {
  Scale: <Scale className="h-4 w-4" />,
  FileText: <FileText className="h-4 w-4" />,
  Link: <Link className="h-4 w-4" />,
  Shield: <Shield className="h-4 w-4" />,
  FileBarChart: <FileBarChart className="h-4 w-4" />,
  CheckSquare: <CheckSquare className="h-4 w-4" />,
  Search: <Search className="h-4 w-4" />,
  CalendarClock: <CalendarClock className="h-4 w-4" />,
  Workflow: <Workflow className="h-4 w-4" />,
  Cpu: <Cpu className="h-4 w-4" />,
};

export const GenerateReportDialog = memo(function GenerateReportDialog() {
  const {
    generateDialogOpen,
    setGenerateDialogOpen,
    selectedTemplate,
    setSelectedTemplate,
  } = useReportStore();

  const [caseId, setCaseId] = useState("");
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");

  const generateReport = useGenerateReport();
  const generateComplianceReport = useGenerateComplianceReport();

  const template = REPORT_TEMPLATES.find((t) => t.report_type === selectedTemplate);

  const handleGenerate = useCallback(async () => {
    if (!caseId.trim() || !title.trim()) {
      toast.add({
        title: "Missing Fields",
        description: "Case ID and title are required.",
        type: "error",
      });
      return;
    }

    try {
      if (selectedTemplate === "compliance_report") {
        await generateComplianceReport.mutateAsync({
          report_type: "chain_of_custody" as ComplianceReportType,
        });
      } else {
        await generateReport.mutateAsync({
          case_id: caseId.trim(),
          title: title.trim(),
          report_type: selectedTemplate || "court_ready",
          notes: notes.trim() || undefined,
        });
      }

      toast.add({
        title: "Report Generated",
        description: `"${title}" has been generated successfully.`,
        type: "success",
      });

      setGenerateDialogOpen(false);
      setCaseId("");
      setTitle("");
      setNotes("");
      setSelectedTemplate(null);
    } catch (error) {
      toast.add({
        title: "Generation Failed",
        description: error instanceof Error ? error.message : "Could not generate report.",
        type: "error",
      });
    }
  }, [
    caseId,
    title,
    notes,
    selectedTemplate,
    generateReport,
    generateComplianceReport,
    setGenerateDialogOpen,
    setSelectedTemplate,
  ]);

  const handleClose = () => {
    setGenerateDialogOpen(false);
    setSelectedTemplate(null);
    setCaseId("");
    setTitle("");
    setNotes("");
  };

  return (
    <Dialog open={generateDialogOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {template && (
              <span className="text-primary">
                {ICON_MAP[template.icon] || <FileText className="h-4 w-4" />}
              </span>
            )}
            Generate Report
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="max-h-[400px]">
          <div className="space-y-4 py-2">
            {template && (
              <div className="p-3 rounded-lg bg-muted/50">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="text-sm font-medium">{template.name}</h4>
                  <Badge variant="outline" className="text-[8px]">
                    {template.report_type}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{template.description}</p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {template.sections.map((s) => (
                    <Badge key={s} variant="secondary" className="text-[8px]">
                      {s}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="caseId" className="text-xs">
                Case ID *
              </Label>
              <Input
                id="caseId"
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
                placeholder="Enter case ID"
                className="h-8 text-xs"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="title" className="text-xs">
                Report Title *
              </Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter report title"
                className="h-8 text-xs"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes" className="text-xs">
                Notes (optional)
              </Label>
              <Input
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Additional notes..."
                className="h-8 text-xs"
              />
            </div>

            {template?.backendGenerated && (
              <div className="flex items-center gap-2 p-2 rounded bg-blue-50 border border-blue-200">
                <AlertTriangle className="h-3.5 w-3.5 text-blue-600 shrink-0" />
                <p className="text-[10px] text-blue-700">
                  This report will be generated by the backend. The backend will compile case data,
                  evidence inventory, chain of custody, and audit information into a court-ready document.
                </p>
              </div>
            )}
          </div>
        </ScrollArea>

        <DialogFooter>
          <Button variant="outline" size="sm" onClick={handleClose}>
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={handleGenerate}
            disabled={!caseId.trim() || !title.trim() || generateReport.isPending || generateComplianceReport.isPending}
          >
            {(generateReport.isPending || generateComplianceReport.isPending) && (
              <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />
            )}
            Generate Report
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
});
