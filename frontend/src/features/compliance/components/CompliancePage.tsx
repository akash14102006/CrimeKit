"use client";

import { Suspense } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Shield,
  RefreshCw,
  Scale,
  Lock,
  FileCheck,
  Clock,
  ShieldCheck,
  Download,
  Loader2,
} from "lucide-react";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { ComplianceKPI } from "../components/ComplianceKPI";
import { GDPRRequestsPanel } from "../components/GDPRRequestsPanel";
import { LegalHoldPanel } from "../components/LegalHoldPanel";
import { RetentionPoliciesPanel } from "../components/RetentionPoliciesPanel";
import { ComplianceTimeline } from "../components/ComplianceTimeline";
import { AuditSummaryPanel } from "../components/AuditSummaryPanel";
import { ExportCenterPanel } from "../components/ExportCenterPanel";
import { useComplianceStore, type ComplianceTab } from "../store/complianceStore";

function ComplianceContent() {
  const { activeTab, setActiveTab } = useComplianceStore();

  const tabs: { key: ComplianceTab; label: string; icon: React.ReactNode }[] = [
    { key: "dashboard", label: "Dashboard", icon: <Shield className="h-3 w-3" /> },
    { key: "gdpr", label: "GDPR", icon: <Scale className="h-3 w-3" /> },
    { key: "legal-hold", label: "Legal Hold", icon: <Lock className="h-3 w-3" /> },
    { key: "retention", label: "Retention", icon: <FileCheck className="h-3 w-3" /> },
    { key: "timeline", label: "Timeline", icon: <Clock className="h-3 w-3" /> },
    { key: "audit", label: "Audit", icon: <ShieldCheck className="h-3 w-3" /> },
    { key: "export", label: "Export", icon: <Download className="h-3 w-3" /> },
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <div className="flex-1 flex flex-col min-w-0">
        <div className="px-6 py-4 border-b space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="h-5 w-5 text-primary" />
              <h1 className="text-lg font-semibold">Compliance & Legal Governance</h1>
            </div>
          </div>

          <ComplianceKPI />

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
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-auto">
          {activeTab === "dashboard" && (
            <ScrollArea className="h-full">
              <div className="p-6 space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <LegalHoldPanel />
                  <RetentionPoliciesPanel />
                </div>
                <ComplianceTimeline />
              </div>
            </ScrollArea>
          )}

          {activeTab === "gdpr" && (
            <ScrollArea className="h-full">
              <div className="p-6 space-y-6">
                <GDPRRequestsPanel />
              </div>
            </ScrollArea>
          )}

          {activeTab === "legal-hold" && (
            <ScrollArea className="h-full">
              <div className="p-6 space-y-6">
                <LegalHoldPanel />
              </div>
            </ScrollArea>
          )}

          {activeTab === "retention" && (
            <ScrollArea className="h-full">
              <div className="p-6 space-y-6">
                <RetentionPoliciesPanel />
              </div>
            </ScrollArea>
          )}

          {activeTab === "timeline" && (
            <ScrollArea className="h-full">
              <div className="p-6 space-y-6">
                <ComplianceTimeline />
              </div>
            </ScrollArea>
          )}

          {activeTab === "audit" && (
            <ScrollArea className="h-full">
              <div className="p-6 space-y-6">
                <AuditSummaryPanel />
              </div>
            </ScrollArea>
          )}

          {activeTab === "export" && (
            <ScrollArea className="h-full">
              <div className="p-6 space-y-6">
                <ExportCenterPanel />
              </div>
            </ScrollArea>
          )}
        </div>
      </div>
    </div>
  );
}

export default function CompliancePage() {
  return (
    <AuthGuard
      allowedRoles={["admin", "investigator", "analyst", "compliance_officer"]}
    >
      <Suspense
        fallback={
          <div className="flex h-[400px] items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        }
      >
        <ComplianceContent />
      </Suspense>
    </AuthGuard>
  );
}
