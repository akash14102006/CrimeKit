"use client";

import { useState, useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  FileText,
  Download,
  Pin,
  PinOff,
  Loader2,
  Hash,
} from "lucide-react";
import { useEvidence } from "@/hooks/queries/useEvidence";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { evidenceService } from "@/services/evidenceService";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";

function formatBytes(bytes: number) {
  if (!bytes) return "0 B";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

function EvidencePreview({ evidenceId, mimeType }: { evidenceId: string; mimeType?: string | null }) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const revokeRef = useRef<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    evidenceService
      .fetchFile(evidenceId)
      .then((blob) => {
        if (cancelled) return;
        const url = URL.createObjectURL(blob);
        revokeRef.current = url;
        setObjectUrl(url);
        setLoading(false);
      })
      .catch(() => {
        if (!cancelled) {
          setError(true);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
      if (revokeRef.current) URL.revokeObjectURL(revokeRef.current);
    };
  }, [evidenceId]);

  if (loading) return <Skeleton className="h-[250px] w-full rounded-lg" />;
  if (error || !objectUrl) {
    return (
      <div className="flex items-center justify-center h-[250px] bg-muted rounded-lg">
        <p className="text-xs text-muted-foreground">Preview unavailable</p>
      </div>
    );
  }

  const mime = mimeType ?? "";
  if (mime.startsWith("image/")) {
    return (
      <div className="flex items-center justify-center bg-muted rounded-lg p-4">
        <img src={objectUrl} alt="evidence" className="max-h-[250px] w-auto rounded" />
      </div>
    );
  }
  if (mime.startsWith("video/")) {
    return <video src={objectUrl} controls className="max-h-[250px] w-full rounded-lg" preload="metadata" />;
  }
  if (mime.startsWith("audio/")) {
    return (
      <div className="flex flex-col items-center justify-center bg-muted rounded-lg p-8">
        <audio src={objectUrl} controls className="w-full max-w-md" preload="metadata" />
      </div>
    );
  }
  if (mime.includes("pdf")) {
    return <iframe src={objectUrl} className="w-full h-[300px] rounded-lg border" title="Evidence Preview" />;
  }
  if (mime.startsWith("text/") || mime.includes("json") || mime.includes("xml")) {
    return (
      <div className="bg-muted rounded-lg p-4 max-h-[300px] overflow-y-auto">
        <TextContent url={objectUrl} />
      </div>
    );
  }
  return (
    <div className="flex items-center justify-center h-[250px] bg-muted rounded-lg">
      <div className="text-center">
        <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
        <p className="text-xs text-muted-foreground">Preview not available for this file type</p>
      </div>
    </div>
  );
}

function TextContent({ url }: { url: string }) {
  const [content, setContent] = useState<string | null>(null);
  useEffect(() => {
    fetch(url)
      .then((r) => r.text())
      .then((text) => setContent(text.length > 50000 ? text.slice(0, 50000) + "\n\n[truncated]" : text))
      .catch(() => setContent("[failed to load]"));
  }, [url]);
  if (!content) return <Skeleton className="h-[100px] w-full" />;
  return <pre className="text-xs font-mono whitespace-pre-wrap break-words">{content}</pre>;
}

export function InvestigationCanvas({ caseId: _caseId }: { caseId: string }) { // eslint-disable-line @typescript-eslint/no-unused-vars
  const { selectedEvidence, pinnedEvidenceIds, pinEvidence, unpinEvidence } =
    useWorkspaceStore();
  const { data: evidenceDetail, isLoading } = useEvidence(selectedEvidence?.id ?? undefined);
  const [downloading, setDownloading] = useState(false);

  const isPinned = selectedEvidence ? pinnedEvidenceIds.includes(selectedEvidence.id) : false;

  const handleDownload = async () => {
    if (!selectedEvidence) return;
    setDownloading(true);
    try {
      await evidenceService.download(selectedEvidence.id, selectedEvidence.filename);
    } catch (err) {
      toast.add({ title: "Download Failed", description: getErrorMessage(err), type: "error" });
    } finally {
      setDownloading(false);
    }
  };

  const handlePinToggle = () => {
    if (!selectedEvidence) return;
    if (isPinned) {
      unpinEvidence(selectedEvidence.id);
    } else {
      pinEvidence(selectedEvidence.id);
    }
  };

  if (!selectedEvidence) {
    return (
      <div className="flex h-full items-center justify-center bg-muted/10">
        <div className="text-center space-y-3">
          <FileText className="h-16 w-16 mx-auto text-muted-foreground opacity-40" />
          <p className="text-sm text-muted-foreground">Select evidence from the Explorer to view details</p>
          <p className="text-xs text-muted-foreground">Click any file in the left panel to inspect it here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center px-4 py-2 border-b gap-2">
        <FileText className="h-4 w-4 text-muted-foreground" />
        <span className="font-medium text-sm truncate flex-1">{selectedEvidence.filename}</span>
        <Button variant="ghost" size="sm" className="h-6 px-2" onClick={handlePinToggle}>
          {isPinned ? <PinOff className="h-3 w-3" /> : <Pin className="h-3 w-3" />}
        </Button>
        <Button variant="ghost" size="sm" className="h-6 px-2" onClick={handleDownload} disabled={downloading}>
          {downloading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Download className="h-3 w-3" />}
        </Button>
      </div>

      <ScrollArea className="flex-1 p-4 space-y-4">
        <EvidencePreview key={selectedEvidence.id} evidenceId={selectedEvidence.id} mimeType={selectedEvidence.mime_type} />

        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-4 w-full" />
            ))}
          </div>
        ) : evidenceDetail && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="space-y-1">
                <span className="text-muted-foreground">Type</span>
                <p className="font-medium">{evidenceDetail.mime_type ?? "Unknown"}</p>
              </div>
              <div className="space-y-1">
                <span className="text-muted-foreground">Size</span>
                <p className="font-medium">{formatBytes(evidenceDetail.size)}</p>
              </div>
              <div className="space-y-1">
                <span className="text-muted-foreground">Uploaded By</span>
                <p className="font-medium">{evidenceDetail.uploaded_by ?? "Unknown"}</p>
              </div>
              <div className="space-y-1">
                <span className="text-muted-foreground">Upload Date</span>
                <p className="font-medium">
                  {evidenceDetail.uploaded_at ? new Date(evidenceDetail.uploaded_at).toLocaleDateString() : "N/A"}
                </p>
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Hash className="h-3 w-3" /> SHA-256
              </span>
              <p className="text-[10px] font-mono break-all bg-muted p-2 rounded">
                {evidenceDetail.sha256}
              </p>
            </div>

            {evidenceDetail.metadata && Object.keys(evidenceDetail.metadata).length > 0 && (
              <div className="space-y-1">
                <span className="text-xs text-muted-foreground">Metadata</span>
                <div className="bg-muted p-2 rounded text-[10px] font-mono space-y-0.5">
                  {Object.entries(evidenceDetail.metadata).map(([key, value]) => (
                    <div key={key} className="flex gap-2">
                      <span className="text-muted-foreground">{key}:</span>
                      <span className="truncate">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
