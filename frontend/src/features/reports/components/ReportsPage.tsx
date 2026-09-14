"use client";

import { Suspense, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  FileText,
  Plus,
  RefreshCw,
  Search,
  Scale,
  Shield,
  History,
  CheckSquare,
  Loader2,
  Filter,
} from "lucide-react";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { ReportTemplateSelector } from "../components/ReportTemplateSelector";
import { GenerateReportDialog } from "../components/GenerateReportDialog";
import { ReportPreview } from "../components/ReportPreview";
import { ReportHistory } from "../components/ReportHistory";
import { ReportDownloadPanel } from "../components/ReportDownloadPanel";
import { useReportStore, type ReportsTab } from "../store/reportStore";
import { useComplianceReports } from "../hooks/useReports";

function ReportsContent() {
  const {
    activeTab,
    setActiveTab,
    previewOpen,
    searchQuery,
    setSearchQuery,
    setGenerateDialogOpen,
    setSelectedTemplate,
  } = useReportStore();

  const { data: complianceData, isLoading: complianceLoading } = useComplianceReports();

  const tabs: { key: ReportsTab; label: string; icon: React.ReactNode; count?: number }[] = [
    { key: "templates", label: "Templates", icon: <FileText className="h-3 w-3" /> },
    { key: "history", label: "History", icon: <History className="h-3 w-3" /> },
    { key: "compliance", label: "Compliance", icon: <CheckSquare className="h-3 w-3" />, count: complianceData?.total },
    { key: "audit", label: "Audit", icon: <Shield className="h-3 w-3" /> },
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <div className="flex-1 flex flex-col min-w-0">
        <div className="px-6 py-4 border-b space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="h-5 w-5 text-primary" />
              <h1 className="text-lg font-semibold">Reports & Documentation</h1>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                className="h-8 text-xs gap-1"
                onClick={() => {
                  setSelectedTemplate(null);
                  setGenerateDialogOpen(true);
                }}
              >
                <Plus className="h-3.5 w-3.5" />
                New Report
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <Search className="h-3 w-3 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search reports..."
                className="h-8 text-xs pl-8"
              />
            </div>
          </div>

          <div className="flex items-center gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-xs transition-colors ${
                  activeTab === tab.key
                    ? "bg-muted font-medium"
                    : "text-muted-foreground hover:bg-muted/50"
                }`}
                onClick={() => setActiveTab(tab.key)}
              >
                {tab.icon}
                {tab.label}
                {tab.count !== undefined && tab.count > 0 && (
                  <Badge variant="secondary" className="text-[8px] ml-0.5">
                    {tab.count}
                  </Badge>
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 flex min-h-0">
          <div className="flex-1 overflow-auto">
            {activeTab === "templates" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <ReportTemplateSelector />
                </div>
              </ScrollArea>
            )}

            {activeTab === "history" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <ReportHistory />
                </div>
              </ScrollArea>
            )}

            {activeTab === "compliance" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <div className="space-y-3">
                    <h3 className="text-sm font-semibold flex items-center gap-2">
                      <CheckSquare className="h-4 w-4" />
                      Compliance Reports
                    </h3>
                    {complianceLoading ? (
                      <div className="flex items-center justify-center py-8">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                      </div>
                    ) : !complianceData || complianceData.reports.length === 0 ? (
                      <div className="text-center py-8">
                        <CheckSquare className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
                        <p className="text-sm font-medium">No Compliance Reports</p>
                        <p className="text-xs text-muted-foreground">
                          Generate compliance reports from the templates tab.
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {complianceData.reports.map((report) => (
                          <div
                            key={report.id}
                            className="p-3 rounded-lg border hover:bg-muted/30 transition-colors"
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <Badge variant="outline" className="text-[8px]">
                                {report.report_type}
                              </Badge>
                              <h4 className="text-xs font-medium">{report.title}</h4>
                            </div>
                            <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                              {report.generated_by && <span>By: {report.generated_by}</span>}
                              {report.generated_at && (
                                <span>{new Date(report.generated_at).toLocaleDateString()}</span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </ScrollArea>
            )}

            {activeTab === "audit" && (
              <ScrollArea className="h-full">
                <div className="p-6 space-y-6">
                  <div className="space-y-3">
                    <h3 className="text-sm font-semibold flex items-center gap-2">
                      <Shield className="h-4 w-4" />
                      Audit Trail
                    </h3>
                    <div className="text-center py-8">
                      <Shield className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
                      <p className="text-sm font-medium">Audit Information</p>
                      <p className="text-xs text-muted-foreground">
                        Audit trail is maintained by the backend. All actions are logged automatically.
                      </p>
                    </div>
                  </div>
                </div>
              </ScrollArea>
            )}
          </div>

          {previewOpen && <ReportPreview />}
        </div>
      </div>

      <GenerateReportDialog />
    </div>
  );
}

export default function ReportsPage() {
  return (
    <AuthGuard
      allowedRoles={["admin", "investigator", "analyst", "evidence_officer", "compliance_officer", "demo_evaluator", "jury_evaluator"]}

    >
      <Suspense
        fallback={
          <div className="flex h-[400px] items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        }
      >
        <ReportsContent />
      </Suspense>
    </AuthGuard>
  );
}
