"use client";

import { memo, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Download,
  FileText,
  File,
  Archive,
  FileJson,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { useExportCase, useGenerateComplianceReport } from "../hooks/useCompliance";
import { toast } from "@/components/ui/toast";
import type { ComplianceReportType } from "@/types/compliance";

const REPORT_TYPES: { type: ComplianceReportType; label: string; description: string }[] = [
  { type: "chain_of_custody", label: "Chain of Custody", description: "Evidence custody documentation" },
  { type: "gdpr", label: "GDPR Report", description: "Data protection compliance" },
  { type: "iso27001", label: "ISO 27001", description: "Information security compliance" },
  { type: "soc2", label: "SOC 2", description: "Service organization controls" },
  { type: "retention", label: "Retention Report", description: "Data retention compliance" },
];

export const ExportCenterPanel = memo(function ExportCenterPanel() {
  const [caseId, setCaseId] = useState("");
  const exportCase = useExportCase();
  const generateReport = useGenerateComplianceReport();

  const handleExportCase = useCallback(async (format: string) => {
    if (!caseId.trim()) {
      toast.add({ title: "Missing Case ID", description: "Enter a case ID to export.", type: "error" });
      return;
    }
    try {
      const response = await exportCase.mutateAsync({
        caseId: caseId.trim(),
        format,
        includesEvidence: true,
        includesAuditTrail: true,
        includesChainOfCustody: true,
      });
      toast.add({ title: "Export Complete", description: `Case exported as ${format.toUpperCase()}.`, type: "success" });
    } catch {
      toast.add({ title: "Export Failed", description: "Could not export case.", type: "error" });
    }
  }, [caseId, exportCase]);

  const handleGenerateCompliance = useCallback(async (type: ComplianceReportType) => {
    try {
      await generateReport.mutateAsync({ report_type: type });
      toast.add({ title: "Report Generated", description: `${type} compliance report generated.`, type: "success" });
    } catch {
      toast.add({ title: "Generation Failed", description: "Could not generate compliance report.", type: "error" });
    }
  }, [generateReport]);

  return (
    <Card>
      <CardHeader className="py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Download className="h-4 w-4" />
          Export Center
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label className="text-xs">Case Export</Label>
            <div className="flex items-center gap-2">
              <Input
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
                placeholder="Enter case ID"
                className="h-8 text-xs flex-1"
              />
              <Button
                variant="outline"
                size="sm"
                className="h-8 text-[10px] gap-1"
                onClick={() => handleExportCase("json")}
                disabled={!caseId.trim() || exportCase.isPending}
              >
                {exportCase.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <FileJson className="h-3 w-3" />}
                JSON
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8 text-[10px] gap-1"
                onClick={() => handleExportCase("zip")}
                disabled={!caseId.trim() || exportCase.isPending}
              >
                <Archive className="h-3 w-3" />
                ZIP
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-xs">Compliance Reports</Label>
            <div className="space-y-1.5">
              {REPORT_TYPES.map((rt) => (
                <div key={rt.type} className="flex items-center justify-between p-2 rounded border hover:bg-muted/30 transition-colors">
                  <div>
                    <span className="text-xs font-medium">{rt.label}</span>
                    <p className="text-[10px] text-muted-foreground">{rt.description}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 text-[10px] gap-1"
                    onClick={() => handleGenerateCompliance(rt.type)}
                    disabled={generateReport.isPending}
                  >
                    {generateReport.isPending ? <Loader2 className="h-2.5 w-2.5 animate-spin" /> : <Download className="h-2.5 w-2.5" />}
                    Generate
                  </Button>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2 p-2 rounded bg-blue-50 border border-blue-200">
            <AlertTriangle className="h-3.5 w-3.5 text-blue-600 shrink-0" />
            <p className="text-[10px] text-blue-700">
              All exports are generated by the backend. Files include cryptographic signatures and audit trail references.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});
