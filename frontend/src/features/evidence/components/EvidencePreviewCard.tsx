"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Image from "next/image";
import { FileText, Download, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { evidenceService } from "@/services/evidenceService";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";
import type { Evidence } from "@/types/evidence";
import { OpenDiskAnalyzerAction } from "./OpenDiskAnalyzerAction";

interface Props {
  evidence: Evidence | undefined;
  isLoading: boolean;
}

function blobLoader({ src }: { src: string }) {
  return src;
}

function TextPreview({ objectUrl }: { objectUrl: string }) {
  const [content, setContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetch(objectUrl)
      .then((r) => r.text())
      .then((text) => {
        if (!cancelled) {
          setContent(text.length > 100_000 ? text.slice(0, 100_000) + "\n\n[truncated — showing first 100 KB]" : text);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setContent("[failed to load text content]");
          setLoading(false);
        }
      });
    return () => { cancelled = true; };
  }, [objectUrl]);

  if (loading) return <Skeleton className="h-[100px] w-full" />;
  return <pre className="text-xs font-mono whitespace-pre-wrap break-words">{content}</pre>;
}

function BrowserPreviewContent({ evidence }: { evidence: Evidence }) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const revokeRef = useRef<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    evidenceService
      .fetchFile(evidence.id)
      .then((blob) => {
        if (cancelled) return;
        const url = URL.createObjectURL(blob);
        revokeRef.current = url;
        setObjectUrl(url);
        setStatus("ready");
      })
      .catch((err) => {
        if (cancelled) return;
        setErrorMsg(getErrorMessage(err, "Failed to load preview"));
        setStatus("error");
      });

    return () => {
      cancelled = true;
    };
  }, [evidence.id]);

  useEffect(() => {
    return () => {
      if (revokeRef.current) URL.revokeObjectURL(revokeRef.current);
    };
  }, []);

  const mime = evidence.mime_type ?? "";

  if (status === "loading") {
    return <Skeleton className="h-[300px] w-full rounded-lg" />;
  }

  if (status === "error" || !objectUrl) {
    return (
      <div className="flex flex-col items-center justify-center bg-muted rounded-lg p-8 text-center">
        <FileText className="h-12 w-12 text-muted-foreground mb-3" />
        <p className="text-sm font-medium mb-1">Preview failed</p>
        <p className="text-xs text-muted-foreground">{errorMsg ?? "Could not load preview."}</p>
      </div>
    );
  }

  if (mime.startsWith("image/")) {
    return (
      <div className="flex items-center justify-center bg-muted rounded-lg p-6">
        <Image
          src={objectUrl}
          alt={evidence.filename}
          width={800}
          height={600}
          loader={blobLoader}
          className="max-h-[300px] w-auto object-contain rounded"
          unoptimized
          priority
        />
      </div>
    );
  }

  if (mime.startsWith("video/")) {
    return (
      <video
        src={objectUrl}
        controls
        className="max-h-[300px] w-full rounded-lg"
        preload="metadata"
      />
    );
  }

  if (mime.startsWith("audio/")) {
    return (
      <div className="flex flex-col items-center justify-center bg-muted rounded-lg p-8">
        <audio
          src={objectUrl}
          controls
          className="w-full max-w-md"
          preload="metadata"
        />
        <p className="mt-3 text-xs text-muted-foreground">{evidence.filename}</p>
      </div>
    );
  }

  if (mime.includes("pdf")) {
    return (
      <iframe
        src={objectUrl}
        className="w-full h-[400px] rounded-lg border"
        title={evidence.filename}
      />
    );
  }

  if (mime.startsWith("text/") || mime.includes("json") || mime.includes("xml") || mime.includes("csv") || mime.includes("markdown") || evidence.filename?.endsWith(".md")) {
    return (
      <div className="bg-muted rounded-lg p-4 max-h-[400px] overflow-y-auto">
        <TextPreview objectUrl={objectUrl} />
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center bg-muted rounded-lg p-8 text-center">
      <FileText className="h-12 w-12 text-muted-foreground mb-3" />
      <p className="text-sm font-medium mb-1">Preview not available</p>
      <p className="text-xs text-muted-foreground mb-4">
        This file type ({mime || "unknown"}) cannot be previewed in the browser.
      </p>
    </div>
  );
}

function PreviewContent({ evidence }: { evidence: Evidence }) {
  const isForensicImage = /\.(e01|ex01|ewf)$/i.test(evidence.filename) ||
    (evidence.metadata as Record<string, unknown> | null | undefined)?.evidence_type === "forensic_disk_image";
  if (!isForensicImage) return <BrowserPreviewContent evidence={evidence} />;

  return (
    <div className="flex flex-col items-center justify-center bg-muted rounded-lg p-8 text-center">
      <FileText className="h-12 w-12 text-muted-foreground mb-3" />
      <p className="text-sm font-medium mb-1">Forensic disk image — preview unavailable.</p>
      <p className="text-xs text-muted-foreground mb-4">E01/EWF evidence must be opened by the TSK Disk Analyzer.</p>
      <OpenDiskAnalyzerAction evidence={evidence} />
    </div>
  );
}

export function EvidencePreviewCard({ evidence, isLoading }: Props) {
  const [downloading, setDownloading] = useState(false);

  const handleDownload = useCallback(async () => {
    if (!evidence) return;
    setDownloading(true);
    try {
      await evidenceService.download(evidence.id, evidence.filename);
    } catch (error) {
      toast.add({
        title: "Download Failed",
        description: getErrorMessage(error, "Could not download evidence file."),
        type: "error",
      });
    } finally {
      setDownloading(false);
    }
  }, [evidence]);

  return (
    <Card className="lg:col-span-2">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>File Preview</CardTitle>
        {evidence && (
          <Button
            variant="outline"
            size="sm"
            className="gap-1"
            onClick={handleDownload}
            disabled={downloading}
          >
            {downloading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Download className="h-3.5 w-3.5" />
            )}
            {downloading ? "Downloading..." : "Download"}
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-[300px] w-full rounded-lg" />
        ) : evidence ? (
          <PreviewContent key={evidence.id} evidence={evidence} />
        ) : null}
      </CardContent>
    </Card>
  );
}
