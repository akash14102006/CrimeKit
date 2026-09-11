import { API } from "@/constants/api-endpoints";
import { api, apiClient } from "@/lib/api-client";
import {
  CustodyAppendRequest,
  CustodyAppendResponse,
  CustodyStatus,
  Evidence,
  EvidenceListResponse,
  EvidenceUploadResponse,
} from "@/types/evidence";

export interface EvidenceListParams {
  page?: number;
  limit?: number;
  search?: string;
  mime_type?: string;
  case_id?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export const evidenceService = {
  list: (params?: EvidenceListParams): Promise<EvidenceListResponse> => {
    const searchParams = new URLSearchParams();
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        if (v !== undefined && v !== null && v !== "") searchParams.set(k, String(v));
      }
    }
    const qs = searchParams.toString();
    return api.get<EvidenceListResponse>(`${API.evidence.list}${qs ? `?${qs}` : ""}`);
  },

  detail: (id: string): Promise<Evidence> =>
    api.get<Evidence>(API.evidence.detail(id)),

  byCase: (caseId: string): Promise<Evidence[]> =>
    api.get<Evidence[]>(API.evidence.byCase(caseId)),

  upload: (
    file: File | Blob,
    caseId?: string,
    onProgress?: (percentCompleted: number) => void,
  ): Promise<EvidenceUploadResponse> =>
    api.upload<EvidenceUploadResponse>(
      API.evidence.upload,
      file,
      caseId ? { case_id: caseId } : undefined,
      onProgress ? { onUploadProgress: onProgress } : undefined,
    ),

  custodyStatus: (id: string): Promise<CustodyStatus> =>
    api.get<CustodyStatus>(API.evidence.custody(id)),

  appendCustody: (
    id: string,
    payload: CustodyAppendRequest,
  ): Promise<CustodyAppendResponse> =>
    api.post<CustodyAppendResponse>(API.evidence.custody(id), payload),

  downloadUrl: (id: string): string => API.evidence.download(id),

  /**
   * Fetch a file with authentication headers and return a Blob.
   * Use this instead of <a href> or <img src> for protected endpoints.
   */
  fetchFile: async (id: string): Promise<Blob> => {
    const response = await apiClient.get(API.evidence.download(id), {
      responseType: "blob",
    });
    return response.data as Blob;
  },

  /**
   * Trigger an authenticated browser download.
   */
  download: async (id: string, filename: string): Promise<void> => {
    const blob = await evidenceService.fetchFile(id);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  /**
   * Get an authenticated object URL for previewing a file (image/video/pdf).
   * Caller must revoke the URL when done.
   */
  previewObjectUrl: async (id: string): Promise<string> => {
    const blob = await evidenceService.fetchFile(id);
    return URL.createObjectURL(blob);
  },

  delete: (id: string): Promise<void> =>
    api.delete<void>(API.evidence.delete(id)),

  reassign: (id: string, caseId: string | null): Promise<{ evidence_id: string; case_id: string | null; old_case_id: string | null }> =>
    api.patch<{ evidence_id: string; case_id: string | null; old_case_id: string | null }>(API.evidence.reassign(id), { case_id: caseId }),

  advancedForensics: {
    results: (evidenceId: string): Promise<{ evidence_id: string; results: Array<{ id: string; processor: string; result: Record<string, unknown>; created_at?: string }>; total: number }> =>
      api.get(`/advanced-forensics/results/${evidenceId}`),
    findings: (evidenceId: string): Promise<{ evidence_id: string; findings: Array<{ id: string; severity: string; description: string; source?: string }>; total: number }> =>
      api.get(`/advanced-forensics/results/${evidenceId}/findings`),
    timeline: (evidenceId: string): Promise<{ evidence_id: string; timeline: Array<{ timestamp: string; event: string; source?: string }>; total: number }> =>
      api.get(`/advanced-forensics/results/${evidenceId}/timeline`),
    entities: (evidenceId: string): Promise<{ evidence_id: string; entities: Array<{ type: string; value: string; confidence?: number }>; total: number }> =>
      api.get(`/advanced-forensics/results/${evidenceId}/entities`),
    integrity: (evidenceId: string): Promise<{ integrity_ok: boolean }> =>
      api.post(`/advanced-forensics/integrity/${evidenceId}`, {}),
  },

  ocr: (evidenceId: string): Promise<{ evidence_id: string; text: string | null; source: string; metadata: Record<string, unknown>; created_at: string | null }> =>
    api.get(`/evidence/${evidenceId}/ocr`),
};
