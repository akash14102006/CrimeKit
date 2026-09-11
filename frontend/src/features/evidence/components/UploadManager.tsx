"use client";

import { useEffect, useRef, useState, type DragEventHandler } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  CheckCircle2,
  Clock3,
  FolderUp,
  Gauge,
  Loader2,
  Pause,
  Play,
  RotateCcw,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";
import { uploadService } from "@/services/uploadService";
import { useUploadStore, type UploadQueueItem } from "@/store/uploadStore";

const DEFAULT_CHUNK_SIZE = 100 * 1024 * 1024;
const MAX_CHUNK_RETRIES = 5;
const MAX_PARALLEL_CHUNKS = 4;
const MAX_CLIENT_FILE_SIZE = Number(process.env.NEXT_PUBLIC_MAX_UPLOAD_SIZE_BYTES || 500 * 1024 * 1024 * 1024);

/** Reduce concurrency for large files to avoid overwhelming the storage backend. */
function effectiveConcurrency(fileSize: number): number {
  if (fileSize > 5 * 1024 * 1024 * 1024) return 2;   // >5 GB
  if (fileSize > 500 * 1024 * 1024) return 3;          // >500 MB
  return MAX_PARALLEL_CHUNKS;                           // <=500 MB
}

function formatBytes(bytes: number) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const index = Math.min(units.length - 1, Math.floor(Math.log(bytes) / Math.log(1024)));
  return `${(bytes / 1024 ** index).toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function formatDuration(seconds: number | null) {
  if (seconds == null || !Number.isFinite(seconds) || seconds < 0) return "Calculating";
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  if (hrs > 0) return `${hrs}h ${mins}m`;
  if (mins > 0) return `${mins}m ${secs}s`;
  return `${secs}s`;
}

function uploadTone(upload: UploadQueueItem) {
  switch (upload.status) {
    case "completed":
      return "text-emerald-500";
    case "failed":
    case "cancelled":
      return "text-destructive";
    case "needs_file":
      return "text-amber-500";
    case "in_progress":
    case "starting":
      return "text-primary";
    default:
      return "text-muted-foreground";
  }
}

interface UploadManagerProps {
  initialCaseId?: string;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  trigger?: React.ReactNode | null;
}

export function UploadManager({ initialCaseId, open: controlledOpen, onOpenChange: controlledOnOpenChange, trigger }: UploadManagerProps) {
  const queryClient = useQueryClient();
  const uploads = useUploadStore((state) => state.uploads);
  const addFiles = useUploadStore((state) => state.addFiles);
  const attachFile = useUploadStore((state) => state.attachFile);
  const updateUpload = useUploadStore((state) => state.updateUpload);
  const applyStartResponse = useUploadStore((state) => state.applyStartResponse);
  const applyStatusResponse = useUploadStore((state) => state.applyStatusResponse);
  const applyCompletion = useUploadStore((state) => state.applyCompletion);
  const removeUpload = useUploadStore((state) => state.removeUpload);
  const clearCompleted = useUploadStore((state) => state.clearCompleted);
  const markHydratedUploadsNeedingFile = useUploadStore((state) => state.markHydratedUploadsNeedingFile);

  const [internalOpen, setInternalOpen] = useState(false);
  const isControlled = controlledOpen !== undefined;
  const open = isControlled ? controlledOpen : internalOpen;
  const setOpen = (val: boolean) => {
    if (isControlled && controlledOnOpenChange) controlledOnOpenChange(val);
    else setInternalOpen(val);
  };
  const [caseId, setCaseId] = useState(initialCaseId || "");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);
  const activeUploadsRef = useRef<Set<string>>(new Set());
  const controllersRef = useRef<Record<string, Map<number, AbortController>>>({});
  const inflightProgressRef = useRef<Record<string, Record<number, number>>>({});
  const completedBytesRef = useRef<Record<string, number>>({});
  const speedSampleRef = useRef<Record<string, { ts: number; bytes: number }>>({});

  useEffect(() => {
    markHydratedUploadsNeedingFile();
    if (folderInputRef.current) {
      folderInputRef.current.setAttribute("webkitdirectory", "");
      folderInputRef.current.setAttribute("directory", "");
    }
  }, [markHydratedUploadsNeedingFile]);

  const getUpload = (id: string) => useUploadStore.getState().uploads.find((upload) => upload.id === id);

  const chunkBytes = (upload: UploadQueueItem, chunkNumber: number) => {
    const start = (chunkNumber - 1) * upload.chunkSize;
    const end = Math.min(upload.size, start + upload.chunkSize);
    return Math.max(0, end - start);
  };

  const recalcStats = (id: string) => {
    const upload = getUpload(id);
    if (!upload) return;
    const inflight = Object.values(inflightProgressRef.current[id] || {}).reduce((sum, value) => sum + value, 0);
    const bytesUploaded = Math.min(upload.size, (completedBytesRef.current[id] || 0) + inflight);
    const progress = upload.size > 0 ? Math.min(100, (bytesUploaded / upload.size) * 100) : 0;
    const now = Date.now();
    const lastSample = speedSampleRef.current[id];
    let speedBps = upload.speedBps;
    if (lastSample && now > lastSample.ts) {
      speedBps = Math.max(0, (bytesUploaded - lastSample.bytes) / ((now - lastSample.ts) / 1000));
    }
    speedSampleRef.current[id] = { ts: now, bytes: bytesUploaded };
    const etaSeconds = speedBps > 0 ? Math.ceil((upload.size - bytesUploaded) / speedBps) : null;
    updateUpload(id, { bytesUploaded, progress, speedBps, etaSeconds });
  };

  const abortUploadControllers = (id: string) => {
    const controllers = controllersRef.current[id];
    if (!controllers) return;
    controllers.forEach((controller) => controller.abort());
    delete controllersRef.current[id];
    delete inflightProgressRef.current[id];
    delete speedSampleRef.current[id];
  };

  const updateCompletedBytes = (id: string) => {
    const upload = getUpload(id);
    if (!upload) return;
    completedBytesRef.current[id] = upload.completedPartNumbers.reduce(
      (sum, chunkNumber) => sum + chunkBytes(upload, chunkNumber),
      0,
    );
    recalcStats(id);
  };

  const delay = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms));

  const uploadChunkWithRetry = async (id: string, chunkNumber: number) => {
    const upload = getUpload(id);
    if (!upload?.file || !upload.backendSessionId) {
      throw new Error("upload session is missing a local file handle");
    }

    const start = (chunkNumber - 1) * upload.chunkSize;
    const end = Math.min(upload.size, start + upload.chunkSize);
    const blob = upload.file.slice(start, end);

    for (let attempt = 1; attempt <= MAX_CHUNK_RETRIES; attempt += 1) {
      const current = getUpload(id);
      if (!current || !current.backendSessionId || current.status === "paused" || current.status === "cancelled") {
        return;
      }

      const controller = new AbortController();
      controllersRef.current[id] ??= new Map<number, AbortController>();
      controllersRef.current[id].set(chunkNumber, controller);
      inflightProgressRef.current[id] ??= {};
      inflightProgressRef.current[id][chunkNumber] = 0;
      updateUpload(id, { currentChunk: chunkNumber, retryCount: Math.max(current.retryCount, attempt - 1) });

      try {
        const result = await uploadService.uploadChunk({
          sessionId: current.backendSessionId,
          chunkNumber,
          chunk: blob,
          signal: controller.signal,
          onProgress: (loaded) => {
            inflightProgressRef.current[id][chunkNumber] = loaded;
            recalcStats(id);
          },
        });

        const refreshed = getUpload(id);
        if (!refreshed) return;
        controllersRef.current[id]?.delete(chunkNumber);
        delete inflightProgressRef.current[id][chunkNumber];
        const completedPartNumbers = Array.from(new Set([...refreshed.completedPartNumbers, chunkNumber])).sort((a, b) => a - b);
        const parts = [...refreshed.parts.filter((part) => part.PartNumber !== chunkNumber), { PartNumber: chunkNumber, ETag: result.etag }].sort(
          (a, b) => a.PartNumber - b.PartNumber,
        );
        updateUpload(id, {
          completedChunks: completedPartNumbers.length,
          completedPartNumbers,
          parts,
          currentChunk: null,
          error: undefined,
          retryCount: Math.max(refreshed.retryCount, attempt - 1),
        });
        updateCompletedBytes(id);
        return;
      } catch (error) {
        controllersRef.current[id]?.delete(chunkNumber);
        delete inflightProgressRef.current[id][chunkNumber];
        const message = getErrorMessage(error, `Chunk ${chunkNumber} failed`);
        const latest = getUpload(id);
        if (!latest || latest.status === "paused" || latest.status === "cancelled") {
          return;
        }
        if (attempt === MAX_CHUNK_RETRIES) {
          updateUpload(id, {
            status: "failed",
            currentChunk: chunkNumber,
            error: message,
            retryCount: Math.max(latest.retryCount, attempt),
            speedBps: 0,
          });
          throw error;
        }
        updateUpload(id, {
          error: `${message}. Retrying chunk ${chunkNumber} (${attempt}/${MAX_CHUNK_RETRIES - 1})`,
          retryCount: Math.max(latest.retryCount, attempt),
        });
        await delay(2 ** attempt * 500);
      }
    }
  };

  const runUpload = async (id: string) => {
    if (activeUploadsRef.current.has(id)) return;
    activeUploadsRef.current.add(id);

    try {
      let upload = getUpload(id);
      if (!upload) return;
      if (!upload.file) {
        updateUpload(id, { status: "needs_file", error: "Reattach the file to resume this persisted upload." });
        return;
      }

      if (!upload.backendSessionId) {
        updateUpload(id, { status: "starting", startedAt: Date.now(), error: undefined });
        const response = await uploadService.start({
          filename: upload.name,
          file_size: upload.size,
          chunk_size: upload.chunkSize || DEFAULT_CHUNK_SIZE,
          case_id: upload.caseId || undefined,
          mime_type: upload.type,
        });
        applyStartResponse(id, response);
      } else {
        const status = await uploadService.status(upload.backendSessionId);
        applyStatusResponse(id, status);
        if (!["completed", "cancelled"].includes(status.status)) {
          const resumed = await uploadService.resume(upload.backendSessionId);
          applyStatusResponse(id, resumed);
        }
      }

      upload = getUpload(id);
      if (!upload) return;
      updateUpload(id, { status: "in_progress", error: undefined, startedAt: upload.startedAt ?? Date.now() });
      updateCompletedBytes(id);

      const reserved = new Set<number>();
      const nextChunkNumber = () => {
        const current = getUpload(id);
        if (!current) return null;
        for (let chunkNumber = 1; chunkNumber <= current.totalChunks; chunkNumber += 1) {
          if (current.completedPartNumbers.includes(chunkNumber) || reserved.has(chunkNumber)) {
            continue;
          }
          reserved.add(chunkNumber);
          return chunkNumber;
        }
        return null;
      };

      const worker = async () => {
        while (true) {
          const current = getUpload(id);
          if (!current || current.status !== "in_progress") return;
          const chunkNumber = nextChunkNumber();
          if (chunkNumber == null) return;
          try {
            await uploadChunkWithRetry(id, chunkNumber);
          } finally {
            reserved.delete(chunkNumber);
          }
        }
      };

      const concurrency = effectiveConcurrency(upload.size);
      await Promise.all(Array.from({ length: concurrency }, () => worker()));

      upload = getUpload(id);
      if (!upload || upload.status !== "in_progress") return;
      if (upload.completedPartNumbers.length !== upload.totalChunks || !upload.backendSessionId) {
        return;
      }

      const completed = await uploadService.complete(upload.backendSessionId, upload.parts);
      applyCompletion(id, completed);
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      queryClient.invalidateQueries({ queryKey: ["workspace"] });
      toast.add({
        title: "Evidence Ingested",
        description: `${upload.name} uploaded and queued for forensic processing.`,
        type: "success",
      });
    } catch (error) {
      const current = getUpload(id);
      if (current && current.status !== "paused" && current.status !== "cancelled") {
        updateUpload(id, {
          status: "failed",
          error: getErrorMessage(error, "Multipart upload failed"),
          speedBps: 0,
          etaSeconds: null,
        });
      }
    } finally {
      activeUploadsRef.current.delete(id);
      abortUploadControllers(id);
    }
  };

  const processIncomingFiles = (files: FileList | File[]) => {
    const incoming = Array.from(files);
    if (incoming.length === 0) return;

    const pending = useUploadStore.getState().uploads.filter((upload) => upload.status === "needs_file");
    const unmatched: File[] = [];

    for (const file of incoming) {
      if (file.size > MAX_CLIENT_FILE_SIZE) {
        toast.add({
          title: "File Too Large",
          description: `${file.name} (${(file.size / (1024 ** 3)).toFixed(1)} GB) exceeds the maximum upload size of ${(MAX_CLIENT_FILE_SIZE / (1024 ** 3)).toFixed(0)} GB. Set NEXT_PUBLIC_MAX_UPLOAD_SIZE_BYTES to increase.`,
          type: "error",
        });
        continue;
      }
      const match = pending.find((upload) => upload.name === file.name && upload.size === file.size && !upload.file);
      if (match) {
        attachFile(match.id, file);
      } else {
        unmatched.push(file);
      }
    }

    if (unmatched.length > 0) {
      addFiles(unmatched, caseId || undefined);
    }
  };

  const startQueue = () => {
    const candidates = useUploadStore.getState().uploads.filter((upload) => ["queued", "paused", "failed"].includes(upload.status) || (upload.status === "needs_file" && !!upload.file));
    candidates.forEach((upload) => {
      void runUpload(upload.id);
    });
  };

  const pauseUpload = (id: string) => {
    updateUpload(id, { status: "paused", speedBps: 0, etaSeconds: null });
    abortUploadControllers(id);
  };

  const resumeUpload = (id: string) => {
    const upload = getUpload(id);
    if (!upload) return;
    if (!upload.file) {
      updateUpload(id, { status: "needs_file", error: "Reattach the original file before resuming." });
      return;
    }
    updateUpload(id, { status: "paused", error: undefined });
    void runUpload(id);
  };

  const cancelUpload = async (id: string) => {
    const upload = getUpload(id);
    if (!upload) return;
    abortUploadControllers(id);
    updateUpload(id, { status: "cancelled", speedBps: 0, etaSeconds: null, error: undefined });
    if (upload.backendSessionId) {
      try {
        await uploadService.cancel(upload.backendSessionId);
      } catch {
        // Best-effort cancellation only.
      }
    }
  };

  const deleteUpload = async (id: string) => {
    const upload = getUpload(id);
    if (upload?.backendSessionId) {
      try {
        await uploadService.remove(upload.backendSessionId);
      } catch {
        // Keep client cleanup even if the backend session is already gone.
      }
    }
    abortUploadControllers(id);
    delete completedBytesRef.current[id];
    delete inflightProgressRef.current[id];
    delete speedSampleRef.current[id];
    removeUpload(id);
  };

  const handleDrop: DragEventHandler<HTMLDivElement> = (event) => {
    event.preventDefault();
    setIsDragging(false);
    if (event.dataTransfer.files?.length) {
      processIncomingFiles(event.dataTransfer.files);
    }
  };

  const activeCount = uploads.filter((upload) => upload.status === "in_progress" || upload.status === "starting").length;
  const pendingCount = uploads.filter((upload) => ["queued", "paused", "failed", "needs_file"].includes(upload.status)).length;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {trigger !== null && (
        trigger ?? (
          <DialogTrigger render={<Button className="gap-2" />}>
            <UploadCloud className="h-4 w-4" />
            Upload Evidence
          </DialogTrigger>
        )
      )}
      <DialogContent className="flex h-[min(92vh,720px)] w-[96vw] max-w-[1100px] flex-col gap-0 overflow-hidden rounded-lg p-0 sm:max-w-[1100px]">
        <DialogHeader className="shrink-0 px-6 pt-6 pb-4">
          <DialogTitle>Enterprise Evidence Ingestion</DialogTitle>
          <DialogDescription>
            Resumable multipart uploads stream 100MB chunks directly to object storage with parallel workers, retry handling, and recovery after interruption.
          </DialogDescription>
        </DialogHeader>

        <div className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-6 pb-6 lg:grid lg:grid-cols-[minmax(0,1fr)_380px] lg:gap-6 lg:overflow-hidden">
          {/* Left: case controls + drop zone + queue stats */}
          <div className="flex min-h-0 min-w-0 flex-col gap-4">
            <div className="shrink-0 rounded-lg border bg-muted/20 p-4">
              <div className="space-y-1.5">
                <Label htmlFor="upload-case-id">Case ID</Label>
                <Input id="upload-case-id" value={caseId} onChange={(event) => setCaseId(event.target.value)} placeholder="Associate new uploads with a case..." />
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <Button type="button" variant="outline" className="min-w-[112px] gap-2" onClick={() => fileInputRef.current?.click()}>
                  <UploadCloud className="h-4 w-4" />
                  Files
                </Button>
                <Button type="button" variant="outline" className="min-w-[112px] gap-2" onClick={() => folderInputRef.current?.click()}>
                  <FolderUp className="h-4 w-4" />
                  Folder
                </Button>
              </div>
            </div>

            <div className="flex min-h-0 flex-1 flex-col gap-4">
              <div
                className={`flex min-h-[320px] flex-1 flex-col items-center justify-center rounded-lg border-2 border-dashed px-8 py-10 text-center transition-colors cursor-pointer ${isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:bg-muted/40"}`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(event) => {
                  event.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
              >
                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-lg border-2 border-dashed border-muted-foreground/30 bg-muted/20">
                  <UploadCloud className="h-7 w-7 text-muted-foreground" />
                </div>
                <p className="text-base font-semibold">Drop forensic artifacts here</p>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
                  E01, EWF, DD, RAW, ISO, TAR, ZIP, PCAP, memory dumps, VM images, mobile images, binary evidence.
                </p>
              </div>

              {/* Queue stats + actions */}
              <div className="shrink-0 rounded-lg border bg-muted/30 px-4 py-3 text-sm">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex flex-wrap gap-x-5 gap-y-1">
                    <span>{uploads.length} queued</span>
                    <span>{activeCount} active</span>
                    <span>{pendingCount} pending</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button type="button" size="sm" variant="outline" onClick={clearCompleted}>
                      Clear Finished
                    </Button>
                    <Button type="button" size="sm" className="gap-2" onClick={startQueue} disabled={uploads.length === 0}>
                      <Play className="h-4 w-4" />
                      Start Queue
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Upload queue list */}
          <div className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-lg border bg-background/40">
            <div className="shrink-0 border-b bg-muted/30 px-4 py-3 text-sm font-medium text-muted-foreground">
              Upload Queue
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3">
              {uploads.length === 0 ? (
                <div className="flex h-full min-h-[320px] items-center justify-center rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
                  No evidence queued yet.
                </div>
              ) : (
                <div className="space-y-2.5">
                  {uploads.map((upload) => (
                    <div key={upload.id} className="rounded-lg border p-3.5">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            {upload.status === "completed" ? (
                              <CheckCircle2 className={`h-3.5 w-3.5 shrink-0 ${uploadTone(upload)}`} />
                            ) : upload.status === "failed" || upload.status === "cancelled" || upload.status === "needs_file" ? (
                              <AlertCircle className={`h-3.5 w-3.5 shrink-0 ${uploadTone(upload)}`} />
                            ) : upload.status === "in_progress" || upload.status === "starting" ? (
                              <Loader2 className={`h-3.5 w-3.5 shrink-0 animate-spin ${uploadTone(upload)}`} />
                            ) : (
                              <UploadCloud className={`h-3.5 w-3.5 shrink-0 ${uploadTone(upload)}`} />
                            )}
                            <p className="truncate text-sm font-medium leading-5">{upload.name}</p>
                          </div>
                          <p className="mt-0.5 break-words text-xs leading-5 text-muted-foreground">
                            {formatBytes(upload.size)} &middot; {upload.completedChunks}/{upload.totalChunks} chunks &middot; {upload.status.replaceAll("_", " ")}
                          </p>
                        </div>
                        <div className="flex shrink-0 gap-1">
                          {upload.status === "in_progress" || upload.status === "starting" ? (
                            <Button type="button" size="sm" variant="outline" className="h-7 w-7 p-0" onClick={() => pauseUpload(upload.id)}>
                              <Pause className="h-3.5 w-3.5" />
                            </Button>
                          ) : null}
                          {upload.status === "paused" || upload.status === "failed" || (upload.status === "needs_file" && upload.file) ? (
                            <Button type="button" size="sm" variant="outline" className="h-7 w-7 p-0" onClick={() => resumeUpload(upload.id)}>
                              {upload.status === "failed" ? <RotateCcw className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
                            </Button>
                          ) : null}
                          {upload.status !== "completed" && upload.status !== "cancelled" ? (
                            <Button type="button" size="sm" variant="outline" className="h-7 w-7 p-0" onClick={() => void cancelUpload(upload.id)}>
                              <X className="h-3.5 w-3.5" />
                            </Button>
                          ) : null}
                          <Button type="button" size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => void deleteUpload(upload.id)}>
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </div>

                      <div className="mt-2 space-y-1.5">
                        <Progress value={upload.progress} className="h-1.5" />
                        <div className="flex flex-wrap gap-x-4 gap-y-0.5 text-xs text-muted-foreground">
                          <span>{upload.progress.toFixed(1)}%</span>
                          <span className="flex items-center gap-1"><Gauge className="h-3 w-3" />{formatBytes(upload.speedBps)}/s</span>
                          <span className="flex items-center gap-1"><Clock3 className="h-3 w-3" />{formatDuration(upload.etaSeconds)}</span>
                          <span>Retry: {upload.retryCount}</span>
                        </div>
                        <div className="flex flex-wrap gap-x-4 gap-y-0.5 text-xs text-muted-foreground">
                          <span>{formatBytes(upload.bytesUploaded)} / {formatBytes(upload.size)}</span>
                          <span>Chunk: {upload.currentChunk ?? "Idle"}</span>
                          <span>Session: {upload.backendSessionId ? "Active" : "Not started"}</span>
                        </div>
                        {upload.warning ? <p className="text-xs text-amber-600">{upload.warning}</p> : null}
                        {upload.status === "needs_file" ? (
                          <p className="text-xs text-amber-600">Reselect same file to resume.</p>
                        ) : null}
                        {upload.error ? <p className="text-xs text-destructive">{upload.error}</p> : null}
                        {upload.evidenceId ? <p className="text-xs text-emerald-600">Evidence ID: {upload.evidenceId}</p> : null}
                        {upload.sha256 ? <p className="break-all text-xs text-muted-foreground">SHA-256: {upload.sha256}</p> : null}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(event) => {
            if (event.target.files) {
              processIncomingFiles(event.target.files);
            }
            event.target.value = "";
          }}
        />

        <input
          ref={folderInputRef}
          type="file"
          multiple
          {...({ webkitdirectory: "", directory: "" } as Record<string, string>)}
          className="hidden"
          onChange={(event) => {
            if (event.target.files) {
              processIncomingFiles(event.target.files);
            }
            event.target.value = "";
          }}
        />

        <DialogFooter className="mx-0 mb-0 shrink-0 px-6">
          <Button type="button" variant="outline" onClick={() => setOpen(false)}>
            Close
          </Button>
          <Button type="button" className="gap-2" onClick={startQueue} disabled={uploads.length === 0}>
            <UploadCloud className="h-4 w-4" />
            Start Uploads
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
