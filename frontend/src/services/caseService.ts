import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import { CaseCreate, CaseListResponse, CaseOut, CaseUpdate } from "@/types/case";

export interface CaseListParams {
  page?: number;
  limit?: number;
  search?: string;
  status?: string;
  priority?: string;
  assigned_to?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export const caseService = {
  list: (params?: CaseListParams): Promise<CaseListResponse> => {
    const searchParams = new URLSearchParams();
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        if (v !== undefined && v !== null && v !== "") searchParams.set(k, String(v));
      }
    }
    const qs = searchParams.toString();
    return api.get<CaseListResponse>(`${API.cases.list}${qs ? `?${qs}` : ""}`);
  },

  detail: (id: string): Promise<CaseOut> =>
    api.get<CaseOut>(API.cases.detail(id)),

  create: (payload: CaseCreate): Promise<CaseOut> =>
    api.post<CaseOut>(API.cases.create, payload),

  update: (id: string, payload: CaseUpdate): Promise<CaseOut> =>
    api.put<CaseOut>(API.cases.update(id), payload),

  patch: (id: string, payload: Partial<CaseUpdate>): Promise<CaseOut> =>
    api.patch<CaseOut>(API.cases.patch(id), payload),

  assign: (id: string, userId: string | null): Promise<CaseOut> =>
    api.patch<CaseOut>(API.cases.assign(id), { assigned_to: userId }),

  remove: (id: string): Promise<void> => api.delete<void>(API.cases.delete(id)),
};
