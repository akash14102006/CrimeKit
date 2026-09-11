"use client";

import { memo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Clock,
  Lock,
  Unlock,
  FileCheck,
  Scale,
  Shield,
  AlertTriangle,
} from "lucide-react";
import { useLegalHolds, useRetentionPolicies, useComplianceReportsList } from "../hooks/useCompliance";

interface TimelineEvent {
  id: string;
  type: "hold_placed" | "hold_released" | "policy_created" | "policy_executed" | "gdpr_request" | "compliance_report" | "audit_event";
  title: string;
  description: string;
  timestamp: string;
  icon: React.ReactNode;
  color: string;
}

const EVENT_ICONS: Record<string, { icon: React.ReactNode; color: string }> = {
  hold_placed: { icon: <Lock className="h-3 w-3" />, color: "bg-amber-100 text-amber-700" },
  hold_released: { icon: <Unlock className="h-3 w-3" />, color: "bg-emerald-100 text-emerald-700" },
  policy_created: { icon: <FileCheck className="h-3 w-3" />, color: "bg-blue-100 text-blue-700" },
  compliance_report: { icon: <Shield className="h-3 w-3" />, color: "bg-violet-100 text-violet-700" },
  gdpr_request: { icon: <Scale className="h-3 w-3" />, color: "bg-orange-100 text-orange-700" },
  audit_event: { icon: <AlertTriangle className="h-3 w-3" />, color: "bg-gray-100 text-gray-700" },
};

export const ComplianceTimeline = memo(function ComplianceTimeline() {
  const { data: holdsData } = useLegalHolds();
  const { data: policiesData } = useRetentionPolicies();
  const { data: reportsData } = useComplianceReportsList();

  const events: TimelineEvent[] = [];

  holdsData?.holds?.forEach((hold) => {
    const config = hold.status === "active" ? EVENT_ICONS.hold_placed : EVENT_ICONS.hold_released;
    events.push({
      id: `hold-${hold.id}`,
      type: hold.status === "active" ? "hold_placed" : "hold_released",
      title: `Legal Hold ${hold.status === "active" ? "Placed" : "Released"}`,
      description: hold.reason,
      timestamp: hold.placed_at || "",
      icon: config.icon,
      color: config.color,
    });
  });

  policiesData?.policies?.forEach((policy) => {
    events.push({
      id: `policy-${policy.id}`,
      type: "policy_created",
      title: `Retention Policy: ${policy.name}`,
      description: `${policy.retention_days} days retention for ${policy.evidence_type || "all evidence"}`,
      timestamp: policy.created_at || "",
      icon: EVENT_ICONS.policy_created.icon,
      color: EVENT_ICONS.policy_created.color,
    });
  });

  reportsData?.reports?.forEach((report) => {
    events.push({
      id: `report-${report.id}`,
      type: "compliance_report",
      title: `Compliance Report: ${report.title}`,
      description: `${report.report_type} report generated`,
      timestamp: report.generated_at || "",
      icon: EVENT_ICONS.compliance_report.icon,
      color: EVENT_ICONS.compliance_report.color,
    });
  });

  events.sort((a, b) => {
    if (!a.timestamp) return 1;
    if (!b.timestamp) return -1;
    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
  });

  return (
    <Card>
      <CardHeader className="py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Clock className="h-4 w-4" />
          Compliance Timeline
        </CardTitle>
      </CardHeader>
      <CardContent>
        {events.length === 0 ? (
          <div className="text-center py-6">
            <Clock className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
            <p className="text-sm font-medium">No Events</p>
            <p className="text-xs text-muted-foreground">Compliance events will appear here.</p>
          </div>
        ) : (
          <ScrollArea className="max-h-[400px]">
            <div className="space-y-3">
              {events.slice(0, 20).map((event) => (
                <div key={event.id} className="flex items-start gap-3">
                  <div className={`p-1.5 rounded-md shrink-0 ${event.color}`}>
                    {event.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-medium">{event.title}</h4>
                    <p className="text-[10px] text-muted-foreground line-clamp-1">{event.description}</p>
                    {event.timestamp && (
                      <span className="text-[9px] text-muted-foreground">
                        {new Date(event.timestamp).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
});
