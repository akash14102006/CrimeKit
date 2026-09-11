"use client";

import { memo } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Scale,
  FileText,
  Link,
  Shield,
  FileBarChart,
  CheckSquare,
  Search,
  CalendarClock,
  Workflow,
  Cpu,
  ArrowRight,
} from "lucide-react";
import { REPORT_TEMPLATES } from "@/types/report";
import { useReportStore } from "../store/reportStore";
import type { ReportTemplate, ReportType } from "@/types/report";

const ICON_MAP: Record<string, React.ReactNode> = {
  Scale: <Scale className="h-5 w-5" />,
  FileText: <FileText className="h-5 w-5" />,
  Link: <Link className="h-5 w-5" />,
  Shield: <Shield className="h-5 w-5" />,
  FileBarChart: <FileBarChart className="h-5 w-5" />,
  CheckSquare: <CheckSquare className="h-5 w-5" />,
  Search: <Search className="h-5 w-5" />,
  CalendarClock: <CalendarClock className="h-5 w-5" />,
  Workflow: <Workflow className="h-5 w-5" />,
  Cpu: <Cpu className="h-5 w-5" />,
};

function TemplateCard({ template }: { template: ReportTemplate }) {
  const { setSelectedTemplate, setGenerateDialogOpen } = useReportStore();

  const handleSelect = () => {
    setSelectedTemplate(template.report_type);
    setGenerateDialogOpen(true);
  };

  return (
    <div
      className="p-4 rounded-lg border hover:bg-muted/30 transition-colors cursor-pointer group"
      onClick={handleSelect}
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-md bg-primary/10 text-primary shrink-0">
          {ICON_MAP[template.icon] || <FileText className="h-5 w-5" />}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="text-sm font-medium">{template.name}</h4>
            {template.backendGenerated && (
              <Badge variant="outline" className="text-[8px]">
                Backend
              </Badge>
            )}
          </div>
          <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
            {template.description}
          </p>
          <div className="flex flex-wrap gap-1">
            {template.sections.slice(0, 4).map((section) => (
              <Badge key={section} variant="secondary" className="text-[8px]">
                {section}
              </Badge>
            ))}
            {template.sections.length > 4 && (
              <Badge variant="secondary" className="text-[8px]">
                +{template.sections.length - 4} more
              </Badge>
            )}
          </div>
        </div>
        <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0 mt-1" />
      </div>
    </div>
  );
}

export const ReportTemplateSelector = memo(function ReportTemplateSelector() {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Report Templates</h3>
        <Badge variant="secondary" className="text-[10px]">
          {REPORT_TEMPLATES.length} templates
        </Badge>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {REPORT_TEMPLATES.map((template) => (
          <TemplateCard key={template.id} template={template} />
        ))}
      </div>
    </div>
  );
});
