import { create } from "zustand";
import { persist } from "zustand/middleware";

import type {
  MultipartPart,
  UploadCompleteResponse,
  UploadSessionStatus,
  UploadSessionStatusResponse,
  UploadStartResponse,
} from "@/types/evidence";

export interface UploadQueueItem {
  id: string;
  name: string;
  size: number;
  type: string;
  caseId?: string;
  relativePath?: string;
  file?: File | null;
  status: UploadSessionStatus;
  progress: number;
  bytesUploaded: number;
  speedBps: number;
  etaSeconds: number | null;
  chunkSize: number;
  totalChunks: number;
  completedChunks: number;
  completedPartNumbers: number[];
  parts: MultipartPart[];
  retryCount: number;
  currentChunk?: number | null;
  error?: string;
  warning?: string;
  sha256?: string;
  md5?: string;
  evidenceId?: string;
  backendSessionId?: string;
  backendUploadId?: string;
  bucket?: string;
  objectKey?: string;
  startedAt?: number;
  updatedAt?: number;
}

interface UploadStore {
  uploads: UploadQueueItem[];
  addFiles: (files: File[], caseId?: string) => void;
  attachFile: (id: string, file: File) => void;
  updateUpload: (id: string, patch: Partial<UploadQueueItem>) => void;
  applyStartResponse: (id: string, response: UploadStartResponse) => void;
  applyStatusResponse: (id: string, response: UploadSessionStatusResponse) => void;
  applyCompletion: (id: string, response: UploadCompleteResponse) => void;
  removeUpload: (id: string) => void;
  clearCompleted: () => void;
  markHydratedUploadsNeedingFile: () => void;
}

function createUploadId(file: File) {
  return [file.name, file.size, file.lastModified, crypto.randomUUID()].join(":");
}

const MAX_CLIENT_FILE_SIZE = Number(process.env.NEXT_PUBLIC_MAX_UPLOAD_SIZE_BYTES || 500 * 1024 * 1024 * 1024);

function adaptiveChunkSize(fileSize: number): number {
  if (fileSize <= 100 * 1024 * 1024) return 5 * 1024 * 1024;       // <= 100MB: 5MB
  if (fileSize <= 1 * 1024 * 1024 * 1024) return 25 * 1024 * 1024; // <= 1GB: 25MB
  if (fileSize <= 10 * 1024 * 1024 * 1024) return 100 * 1024 * 1024; // <= 10GB: 100MB
  if (fileSize <= 50 * 1024 * 1024 * 1024) return 200 * 1024 * 1024; // <= 50GB: 200MB
  return 500 * 1024 * 1024;                                         // > 50GB: 500MB
}

function toQueueItem(file: File, caseId?: string): UploadQueueItem {
  const chunkSize = adaptiveChunkSize(file.size);
  return {
    id: createUploadId(file),
    name: file.name,
    size: file.size,
    type: file.type || "application/octet-stream",
    caseId,
    relativePath: (file as File & { webkitRelativePath?: string }).webkitRelativePath || undefined,
    file,
    status: "queued",
    progress: 0,
    bytesUploaded: 0,
    speedBps: 0,
    etaSeconds: null,
    chunkSize,
    totalChunks: Math.max(1, Math.ceil(file.size / chunkSize)),
    completedChunks: 0,
    completedPartNumbers: [],
    parts: [],
    retryCount: 0,
    currentChunk: null,
    warning: file.size >= 5 * 1024 * 1024 * 1024
      ? `Large forensic artifact (${(file.size / (1024 ** 3)).toFixed(1)} GB). Using ${(chunkSize / (1024 * 1024)).toFixed(0)}MB chunks with parallel workers.`
      : undefined,
    updatedAt: Date.now(),
  };
}

export const useUploadStore = create<UploadStore>()(
  persist(
    (set) => ({
      uploads: [],

      addFiles: (files, caseId) =>
        set((state) => ({
          uploads: [
            ...state.uploads,
            ...files.map((file) => toQueueItem(file, caseId)),
          ],
        })),

      attachFile: (id, file) =>
        set((state) => ({
          uploads: state.uploads.map((upload) =>
            upload.id === id
              ? {
                  ...upload,
                  file,
                  size: file.size,
                  type: file.type || upload.type,
                  status: upload.status === "needs_file" ? "paused" : upload.status,
                  updatedAt: Date.now(),
                }
              : upload,
          ),
        })),

      updateUpload: (id, patch) =>
        set((state) => ({
          uploads: state.uploads.map((upload) =>
            upload.id === id ? { ...upload, ...patch, updatedAt: Date.now() } : upload,
          ),
        })),

      applyStartResponse: (id, response) =>
        set((state) => ({
          uploads: state.uploads.map((upload) =>
            upload.id === id
              ? {
                  ...upload,
                  backendSessionId: response.session_id,
                  backendUploadId: response.upload_id,
                  chunkSize: response.chunk_size,
                  totalChunks: response.total_chunks,
                  bucket: response.bucket,
                  objectKey: response.object_key,
                  status: "in_progress",
                  startedAt: upload.startedAt ?? Date.now(),
                  updatedAt: Date.now(),
                }
              : upload,
          ),
        })),

      applyStatusResponse: (id, response) =>
        set((state) => ({
          uploads: state.uploads.map((upload) => {
            if (upload.id !== id) return upload;
            const bytesUploaded = (response.chunks ?? []).reduce((sum, chunk) => sum + (chunk.status === "uploaded" ? chunk.size : 0), 0);
            return {
              ...upload,
              backendSessionId: response.id,
              backendUploadId: response.upload_id,
              bucket: response.bucket,
              objectKey: response.object_key,
              chunkSize: response.chunk_size,
              totalChunks: response.total_chunks,
              completedChunks: response.completed_chunks,
              completedPartNumbers: response.completed_part_numbers,
              parts: response.parts,
              status: upload.file ? (response.status as UploadSessionStatus) : "needs_file",
              bytesUploaded,
              progress: response.file_size > 0 ? Math.min(100, (bytesUploaded / response.file_size) * 100) : 0,
              error: response.error_message || undefined,
              sha256: response.sha256 || undefined,
              md5: response.md5 || undefined,
              evidenceId: response.evidence_id || undefined,
              updatedAt: Date.now(),
            };
          }),
        })),

      applyCompletion: (id, response) =>
        set((state) => ({
          uploads: state.uploads.map((upload) =>
            upload.id === id
              ? {
                  ...upload,
                  status: "completed",
                  progress: 100,
                  bytesUploaded: upload.size,
                  completedChunks: upload.totalChunks,
                  evidenceId: response.evidence_id,
                  sha256: response.sha256,
                  md5: response.md5 || undefined,
                  speedBps: 0,
                  etaSeconds: 0,
                  currentChunk: null,
                  updatedAt: Date.now(),
                }
              : upload,
          ),
        })),

      removeUpload: (id) =>
        set((state) => ({ uploads: state.uploads.filter((upload) => upload.id !== id) })),

      clearCompleted: () =>
        set((state) => ({
          uploads: state.uploads.filter((upload) => !["completed", "cancelled"].includes(upload.status)),
        })),

      markHydratedUploadsNeedingFile: () =>
        set((state) => ({
          uploads: state.uploads.map((upload) =>
            ["completed", "cancelled"].includes(upload.status) || upload.file
              ? upload
              : {
                  ...upload,
                  status: "needs_file",
                  speedBps: 0,
                  etaSeconds: null,
                  currentChunk: null,
                },
          ),
        })),
    }),
    {
      name: "crimekit-upload-queue",
      partialize: (state) => ({
        uploads: state.uploads.map(({ file, ...upload }) => upload),
      }),
    },
  ),
);
