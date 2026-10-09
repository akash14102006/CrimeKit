import { API } from "@/constants/api-endpoints";
import { api } from "@/lib/api-client";

export interface AIQueryRequest {
  query: string;
  case_id?: string;
  top_k?: number;
}

export interface AIQueryResult {
  document_id: string;
  score: number;
  text?: string;
  snippet?: string;
  evidence_id?: string;
  metadata?: Record<string, unknown>;
}

export interface AIQueryResponse {
  query: string;
  results: AIQueryResult[];
}

export interface CrossCorrelateRequest {
  evidence_ids?: string[];
  case_id?: string;
  max_results?: number;
}

export interface CrossCorrelateResult {
  evidence_id: string;
  related_evidence_id: string;
  similarity: number;
  reason: string;
  shared_attributes?: string[];
}

export interface EntitySearchRequest {
  query: string;
  entity_type?: string;
  case_id?: string;
  limit?: number;
}

export interface EntitySearchResult {
  name: string;
  type: string;
  count?: number;
  sources?: string[];
}

export interface RelationshipSearchRequest {
  entity_id?: string;
  entity_name?: string;
  entity_type?: string;
  max_depth?: number;
  relationship_types?: string[];
  case_id?: string;
  limit?: number;
}

export interface RelationshipResult {
  source: string;
  target: string;
  type: string;
  confidence?: number;
  evidence_id?: string;
}

export interface TimelineSearchRequest {
  start_date?: string;
  end_date?: string;
  case_id?: string;
  entity_ids?: string[];
  limit?: number;
}

export const aiService = {
  query: (payload: AIQueryRequest): Promise<AIQueryResponse> =>
    api.post<AIQueryResponse>(API.ai.query, payload),

  ingest: (payload: {
    text: string;
    metadata?: Record<string, unknown>;
  }): Promise<{ document_id: string; embedding_id: string }> =>
    api.post<{ document_id: string; embedding_id: string }>(
      API.ai.ingest,
      payload,
    ),

  document: (docId: string): Promise<{ id: string; text: string }> =>
    api.get<{ id: string; text: string }>(API.ai.document(docId)),

  crossCorrelate: (
    payload: CrossCorrelateRequest,
  ): Promise<CrossCorrelateResult[]> =>
    api.post<CrossCorrelateResult[]>(
      API.search.crossCorrelate,
      payload,
    ),

  searchEntities: (
    payload: EntitySearchRequest,
  ): Promise<EntitySearchResult[]> =>
    api.post<EntitySearchResult[]>(API.search.entities, payload),

  searchRelationships: (
    payload: RelationshipSearchRequest,
  ): Promise<RelationshipResult[]> =>
    api.post<RelationshipResult[]>(API.search.relationships, payload),

  searchTimeline: (
    payload: TimelineSearchRequest,
  ): Promise<
    Array<{
      id: string;
      timestamp: string;
      title: string;
      description?: string;
      source?: string;
      evidence_id?: string;
    }>
  > =>
    api.post<
      Array<{
        id: string;
        timestamp: string;
        title: string;
        description?: string;
        source?: string;
        evidence_id?: string;
      }>
    >(API.search.timeline, payload),

  // ── Multi-Agent Session & Turn Management ──
  getAgents: (): Promise<BackendAgentMetadata[]> =>
    api.get<BackendAgentMetadata[]>(API.ai.agents),

  createSession: (payload: {
    case_id: string;
    agent_id: string;
    title?: string;
  }): Promise<BackendSessionResponse> =>
    api.post<BackendSessionResponse>(API.ai.sessions, payload),

  listSessions: (params: {
    case_id: string;
    agent_id?: string;
  }): Promise<{ items: BackendSessionResponse[]; total: number }> =>
    api.get<{ items: BackendSessionResponse[]; total: number }>(API.ai.sessions, {
      params,
    }),

  getSession: (sessionId: string): Promise<BackendSessionResponse> =>
    api.get<BackendSessionResponse>(API.ai.sessionDetail(sessionId)),

  getSessionMessages: (sessionId: string): Promise<BackendMessageResponse[]> =>
    api.get<BackendMessageResponse[]>(API.ai.sessionMessages(sessionId)),

  sendMessage: (
    sessionId: string,
    message: string,
  ): Promise<BackendChatTurnResponse> =>
    api.post<BackendChatTurnResponse>(API.ai.sessionMessages(sessionId), {
      message,
    }),
};

export interface BackendAgentMetadata {
  id: string;
  name: string;
  short_name: string;
  tagline: string;
  description: string;
  icon: string;
  category: string;
  status: string;
  capabilities: string[];
  tools: string[];
  suggested_questions: string[];
}

export interface BackendSessionResponse {
  id: string;
  case_id: string;
  agent_id: string;
  user_id?: string;
  title: string;
  status: string;
  pinned: boolean;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface BackendMessageResponse {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  agent_id?: string;
  created_at?: string;
  metadata?: {
    tool_executions?: Array<{
      id: string;
      tool_name: string;
      display_name: string;
      status: "pending" | "running" | "completed" | "failed";
      started_at?: number;
      completed_at?: number;
      output_snippet?: string;
    }>;
    findings?: Array<{
      id: string;
      title: string;
      description: string;
      confidence: number;
      status: "supported" | "contradicted" | "needs_review" | "insufficient_evidence";
      agent_id: string;
      evidence_refs: string[];
      subgraph_nodes?: string[];
    }>;
    evidence_refs?: string[];
    confidence?: number;
    handoff?: {
      source_agent: string;
      target_agent: string;
      reason: string;
      context_summary?: string;
    };
  };
}

export interface BackendChatTurnResponse {
  session_id: string;
  user_message: BackendMessageResponse;
  message: BackendMessageResponse;
  agent: {
    id: string;
    name: string;
    category?: string;
    icon?: string;
  };
  tool_executions: Array<{
    id: string;
    tool_name: string;
    display_name: string;
    status: "pending" | "running" | "completed" | "failed";
    started_at?: number;
    completed_at?: number;
    output_snippet?: string;
  }>;
  findings: Array<{
    id: string;
    title: string;
    description: string;
    confidence: number;
    status: "supported" | "contradicted" | "needs_review" | "insufficient_evidence";
    agent_id: string;
    evidence_refs: string[];
    subgraph_nodes?: string[];
  }>;
  evidence_refs: string[];
  confidence?: number;
  handoff?: {
    source_agent: string;
    target_agent: string;
    reason: string;
    context_summary?: string;
  };
}

