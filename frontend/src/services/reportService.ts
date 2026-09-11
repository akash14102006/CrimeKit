import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import type { Report, ReportCreateRequest } from "@/types/report";

export interface ReportCreateRequestLegacy {
  case_id: string;
  title: string;
  report_type?: string;
  notes?: string;
}

export interface ReportOut {
  id: string;
  case_id: string;
  title: string;
  report_type: string;
  status: string;
  content_markdown: string;
  created_by: string;
  created_at: string;
}

export const reportService = {
  create: (payload: ReportCreateRequest): Promise<Report> =>
    api.post<Report>(API.reports.create, payload),

  byCase: (caseId: string): Promise<Report[]> =>
    api.get<Report[]>(API.reports.byCase(caseId)),

  detail: (reportId: string): Promise<Report> =>
    api.get<Report>(API.reports.detail(reportId)),

  delete: (reportId: string): Promise<{ detail: string }> =>
    api.delete<{ detail: string }>(API.reports.delete(reportId)),

  exportPdf: (reportId: string): Promise<Blob> =>
    apiClient.get(API.reports.exportPdf(reportId), { responseType: "blob" }).then((r) => r.data),

  exportDocx: (reportId: string): Promise<Blob> =>
    apiClient.get(API.reports.exportDocx(reportId), { responseType: "blob" }).then((r) => r.data),

  exportJson: (reportId: string): Promise<Blob> =>
    apiClient.get(API.reports.exportJson(reportId), { responseType: "blob" }).then((r) => r.data),

  exportZip: (reportId: string): Promise<Blob> =>
    apiClient.get(API.reports.exportZip(reportId), { responseType: "blob" }).then((r) => r.data),
};

import apiClient from "@/lib/api-client";
