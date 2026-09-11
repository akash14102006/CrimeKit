import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";
import { InvestigationWorkspace } from "@/types/workspace";

export const workspaceService = {
  detail: (caseId: string): Promise<InvestigationWorkspace> =>
    api.get<InvestigationWorkspace>(API.workspace.detail(caseId)),

  evidence: (caseId: string): Promise<InvestigationWorkspace["evidence"]> =>
    api.get<InvestigationWorkspace["evidence"]>(API.workspace.evidence(caseId)),

  custody: (caseId: string): Promise<InvestigationWorkspace["custody"]> =>
    api.get<InvestigationWorkspace["custody"]>(API.workspace.custody(caseId)),

  timeline: (caseId: string): Promise<InvestigationWorkspace["timeline"]> =>
    api.get<InvestigationWorkspace["timeline"]>(API.workspace.timeline(caseId)),

  progress: (caseId: string): Promise<InvestigationWorkspace["progress"]> =>
    api.get<InvestigationWorkspace["progress"]>(API.workspace.progress(caseId)),

  risks: (caseId: string): Promise<InvestigationWorkspace["risk_indicators"]> =>
    api.get<InvestigationWorkspace["risk_indicators"]>(API.workspace.risks(caseId)),

  kgSummary: (caseId: string): Promise<InvestigationWorkspace["knowledge_graph"]> =>
    api.get<InvestigationWorkspace["knowledge_graph"]>(
      API.workspace.kgSummary(caseId),
    ),

  aiFindings: (caseId: string): Promise<InvestigationWorkspace["ai_findings"]> =>
    api.get<InvestigationWorkspace["ai_findings"]>(
      API.workspace.aiFindings(caseId),
    ),

  courtReport: (caseId: string): Promise<InvestigationWorkspace["court_report"]> =>
    api.get<InvestigationWorkspace["court_report"]>(
      API.workspace.courtReport(caseId),
    ),
};
