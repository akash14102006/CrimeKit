import apiClient, { api } from "@/lib/api-client";
import { API } from "@/constants/api-endpoints";
import type {
  MultipartPart,
  UploadChunkResult,
  UploadCompleteResponse,
  UploadSessionStatusResponse,
  UploadStartRequest,
  UploadStartResponse,
} from "@/types/evidence";

export interface UploadChunkRequest {
  sessionId: string;
  chunkNumber: number;
  chunk: Blob;
  chunkSha256?: string;
  signal?: AbortSignal;
  onProgress?: (loaded: number, total: number) => void;
}

export const uploadService = {
  start: async (payload: UploadStartRequest) => {
    const response = await apiClient.post<UploadStartResponse>(API.uploads.start, payload, {
      timeout: 120_000,
    });
    return response.data;
  },

  uploadChunk: async ({
    sessionId,
    chunkNumber,
    chunk,
    chunkSha256,
    signal,
    onProgress,
  }: UploadChunkRequest) => {
    const form = new FormData();
    form.append("session_id", sessionId);
    form.append("chunk_number", String(chunkNumber));
    if (chunkSha256) {
      form.append("chunk_sha256", chunkSha256);
    }
    form.append("chunk", chunk, `chunk-${chunkNumber}`);

    const response = await apiClient.post<UploadChunkResult>(API.uploads.chunk, form, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 600_000,
      signal,
      onUploadProgress: (event) => {
        if (onProgress) {
          onProgress(event.loaded, event.total ?? chunk.size);
        }
      },
    });

    return response.data;
  },

  complete: async (sessionId: string, parts: MultipartPart[]) => {
    const response = await apiClient.post<UploadCompleteResponse>(
      `${API.uploads.complete}?session_id=${encodeURIComponent(sessionId)}`,
      { parts },
      { timeout: 600_000 },
    );
    return response.data;
  },

  cancel: (sessionId: string) =>
    api.post<{ session_id: string; status: string }>(`${API.uploads.cancel}?session_id=${encodeURIComponent(sessionId)}`),

  status: (uploadId: string) =>
    api.get<UploadSessionStatusResponse>(API.uploads.status(uploadId)),

  resume: (sessionId: string) =>
    api.post<UploadSessionStatusResponse>(`${API.uploads.resume}?session_id=${encodeURIComponent(sessionId)}`),

  remove: (uploadId: string) => api.delete<{ deleted: boolean; upload_id: string }>(API.uploads.delete(uploadId)),
};
