"use client";

import { memo, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  X,
  Download,
  FileText,
  Scale,
  Copy,
  ExternalLink,
} from "lucide-react";
import { useReportStore } from "../store/reportStore";
import type { Report } from "@/types/report";

function renderMarkdown(md: string): string {
  return md
    .replace(/^# (.+)$/gm, '<h1 class="text-xl font-bold mb-3 mt-4">$1</h1>')
    .replace(/^## (.+)$/gm, '<h2 class="text-lg font-semibold mb-2 mt-3">$1</h2>')
    .replace(/^### (.+)$/gm, '<h3 class="text-sm font-medium mb-1 mt-2">$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold">$1</strong>')
    .replace(/`(.+?)`/g, '<code class="text-xs bg-muted px-1 py-0.5 rounded font-mono">$1</code>')
    .replace(/^- (.+)$/gm, '<li class="text-xs ml-4 list-disc">$1</li>')
    .replace(/^(?!<[hl]|<li|<code|<strong)(.+)$/gm, '<p class="text-xs mb-1">$1</p>')
    .replace(/\n{2,}/g, '\n');
}

export const ReportPreview = memo(function ReportPreview() {
  const { selectedReport, previewOpen, setPreviewOpen } = useReportStore();

  const htmlContent = useMemo(
    () => (selectedReport ? renderMarkdown(selectedReport.content_markdown) : ""),
    [selectedReport],
  );

  if (!previewOpen || !selectedReport) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(selectedReport.content_markdown);
  };

  return (
    <div className="w-[450px] border-l flex flex-col bg-background shrink-0">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          <h3 className="text-sm font-semibold">Report Preview</h3>
          <Badge variant="outline" className="text-[9px]">
            {selectedReport.report_type}
          </Badge>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={handleCopy}>
            <Copy className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => setPreviewOpen(false)}>
            <X className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          <div className="space-y-2">
            <h4 className="text-sm font-semibold">{selectedReport.title}</h4>
            <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
              <span>ID: {selectedReport.id.slice(0, 8)}</span>
              <span>By: {selectedReport.created_by}</span>
              <span>{new Date(selectedReport.created_at).toLocaleDateString()}</span>
            </div>
          </div>

          <div
            className="prose prose-xs max-w-none"
            dangerouslySetInnerHTML={{ __html: htmlContent }}
          />

          <div className="flex items-center gap-2 pt-4 border-t">
            <Badge variant="secondary" className="text-[10px]">
              {selectedReport.status}
            </Badge>
            <span className="text-[10px] text-muted-foreground">
              {selectedReport.content_markdown.length} chars
            </span>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
});
