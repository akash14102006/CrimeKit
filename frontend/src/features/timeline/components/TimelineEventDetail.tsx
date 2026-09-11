"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  X,
  ExternalLink,
  FileText,
  Clock,
  Tag,
  ArrowRight,
  ArrowLeft,
} from "lucide-react";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { useRouter } from "next/navigation";
import type { TimelineEvent } from "@/types/timeline";

interface Props {
  event: TimelineEvent | null;
  onClose: () => void;
  onNavigate: (direction: "prev" | "next") => void;
  hasPrev: boolean;
  hasNext: boolean;
}

const SOURCE_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  forensic_engine: { bg: "bg-blue-100", text: "text-blue-800", label: "Forensic Engine" },
  text_extraction: { bg: "bg-purple-100", text: "text-purple-800", label: "Text Extraction" },
  ocr: { bg: "bg-cyan-100", text: "text-cyan-800", label: "OCR" },
  evidence: { bg: "bg-emerald-100", text: "text-emerald-800", label: "Evidence" },
  processing: { bg: "bg-orange-100", text: "text-orange-800", label: "Processing" },
  custody: { bg: "bg-amber-100", text: "text-amber-800", label: "Custody" },
  ai: { bg: "bg-pink-100", text: "text-pink-800", label: "AI Analysis" },
  system: { bg: "bg-gray-100", text: "text-gray-800", label: "System" },
};

export function TimelineEventDetail({ event, onClose, onNavigate, hasPrev, hasNext }: Props) {
  const { selectEvidence } = useWorkspaceStore();
  const router = useRouter();

  if (!event) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <div className="text-center space-y-2">
          <Clock className="h-10 w-10 mx-auto text-muted-foreground opacity-40" />
          <p className="text-xs text-muted-foreground">Select an event to view details</p>
        </div>
      </div>
    );
  }

  const sourceStyle = SOURCE_STYLES[event.source] ?? SOURCE_STYLES.system;
  const meta = (event.metadata ?? {}) as Record<string, unknown>;

  const handleEvidenceClick = () => {
    if (event.evidence_id) {
      selectEvidence(null);
      router.push(`/evidence/${event.evidence_id}`);
    }
  };

  const handleCaseClick = () => {
    if (event.case_id) {
      router.push(`/workspace/${event.case_id}`);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b">
        <div className="flex items-center gap-2 min-w-0">
          <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
          <span className="font-medium text-sm truncate">Event Details</span>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" className="h-6 px-2" onClick={() => onNavigate("prev")} disabled={!hasPrev}>
            <ArrowLeft className="h-3 w-3" />
          </Button>
          <Button variant="ghost" size="sm" className="h-6 px-2" onClick={() => onNavigate("next")} disabled={!hasNext}>
            <ArrowRight className="h-3 w-3" />
          </Button>
          <Button variant="ghost" size="sm" className="h-6 w-6 p-0" onClick={onClose}>
            <X className="h-3 w-3" />
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4 space-y-4">
        <div>
          <h3 className="text-sm font-semibold leading-tight">{event.title}</h3>
          <p className="text-xs text-muted-foreground mt-1">{event.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="space-y-1">
            <span className="text-muted-foreground">Source</span>
            <Badge variant="outline" className={`${sourceStyle.bg} ${sourceStyle.text} text-[10px]`}>
              {sourceStyle.label}
            </Badge>
          </div>
          <div className="space-y-1">
            <span className="text-muted-foreground">Timestamp</span>
            <p className="font-medium">
              {event.timestamp ? new Date(event.timestamp).toLocaleString() : "N/A"}
            </p>
          </div>
        </div>

        {event.evidence_id && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground flex items-center gap-1">
              <Tag className="h-3 w-3" /> Evidence
            </span>
            <Button
              variant="link"
              size="sm"
              className="h-auto p-0 text-xs font-mono"
              onClick={handleEvidenceClick}
            >
              {event.evidence_id}
              <ExternalLink className="h-3 w-3 ml-1" />
            </Button>
          </div>
        )}

        {event.case_id && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground flex items-center gap-1">
              <Tag className="h-3 w-3" /> Case
            </span>
            <Button
              variant="link"
              size="sm"
              className="h-auto p-0 text-xs font-mono"
              onClick={handleCaseClick}
            >
              {event.case_id}
              <ExternalLink className="h-3 w-3 ml-1" />
            </Button>
          </div>
        )}

        {event.id && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Event ID</span>
            <p className="text-[10px] font-mono break-all bg-muted p-2 rounded">{event.id}</p>
          </div>
        )}

        {Object.keys(meta).length > 0 && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Metadata</span>
            <div className="bg-muted p-2 rounded text-[10px] font-mono space-y-0.5">
              {Object.entries(meta).map(([key, value]) => (
                <div key={key} className="flex gap-2">
                  <span className="text-muted-foreground">{key}:</span>
                  <span className="truncate">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
