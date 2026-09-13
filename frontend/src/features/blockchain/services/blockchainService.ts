import { api } from "@/lib/api-client";
import { env } from "@/config/env";

const API = env.apiBaseUrl;

export interface AnchorRecord {
  proof_id: string;
  status: string;
  tx_hash?: string;
  block_number?: number;
  merkle_root: string;
  network: string;
  contract_address?: string;
  anchored_at?: string;
  created_at: string;
}

export interface VerificationReport {
  evidence_id: string;
  evidence_hash_match: boolean;
  commitment_valid: boolean;
  merkle_proof_valid: boolean;
  blockchain_confirmed: boolean;
  overall_result: string;
  details: Record<string, unknown>;
}

export interface ProofBundle {
  protocol: string;
  version: number;
  evidence_id: string;
  evidence_sha256: string;
  commitment_hash: string;
  merkle_proof: {
    leaf_index: number;
    siblings: string[];
    root: string;
  };
  blockchain: {
    network: string;
    chain_id: number;
    contract_address: string;
    tx_hash: string;
    block_number: number;
    timestamp: string;
  };
}

export interface BlockchainStats {
  total_anchors: number;
  pending_anchors: number;
  total_batches: number;
  total_commitments: number;
  network: string;
}

export interface MerkleBatchInfo {
  id: string;
  merkle_root: string;
  leaf_count: number;
  status: string;
  created_at: string;
  anchored_at?: string;
}

export const blockchainService = {
  anchorEvidence: async (evidenceId: string): Promise<AnchorRecord> => {
    const response = await api.post<AnchorRecord>(`${API}/api/v1/blockchain/anchor`, {
      evidence_id: evidenceId,
    });
    return response;
  },

  anchorBatch: async (): Promise<{ batch_id: string; merkle_root: string; leaf_count: number }> => {
    const response = await api.post<{ batch_id: string; merkle_root: string; leaf_count: number }>(
      `${API}/api/v1/blockchain/anchor/batch`
    );
    return response;
  },

  getAnchor: async (proofId: string): Promise<AnchorRecord> => {
    const response = await api.get<AnchorRecord>(`${API}/api/v1/blockchain/anchor/${proofId}`);
    return response;
  },

  getAnchorStatus: async (proofId: string): Promise<{ status: string; tx_hash?: string; block_number?: number }> => {
    const response = await api.get<{ status: string; tx_hash?: string; block_number?: number }>(
      `${API}/api/v1/blockchain/anchor/${proofId}/status`
    );
    return response;
  },

  getProofBundle: async (evidenceId: string): Promise<ProofBundle> => {
    const response = await api.get<ProofBundle>(`${API}/api/v1/blockchain/proof/${evidenceId}`);
    return response;
  },

  verifyEvidence: async (evidenceId: string): Promise<VerificationReport> => {
    const response = await api.post<VerificationReport>(`${API}/api/v1/blockchain/verify`, {
      evidence_id: evidenceId,
    });
    return response;
  },

  getMerkleBatches: async (): Promise<MerkleBatchInfo[]> => {
    const response = await api.get<MerkleBatchInfo[]>(`${API}/api/v1/blockchain/batches`);
    return response;
  },

  getProvenance: async (evidenceId: string): Promise<{
    evidence_id: string;
    timeline: Array<{
      step: string;
      hash?: string;
      tool?: string;
      timestamp: string;
      details: Record<string, unknown>;
    }>;
  }> => {
    const response = await api.get<{
      evidence_id: string;
      timeline: Array<{
        step: string;
        hash?: string;
        tool?: string;
        timestamp: string;
        details: Record<string, unknown>;
      }>;
    }>(`${API}/api/v1/blockchain/provenance/${evidenceId}`);
    return response;
  },

  getStats: async (): Promise<BlockchainStats> => {
    const response = await api.get<BlockchainStats>(`${API}/api/v1/blockchain/stats`);
    return response;
  },

  getProtocol: async (): Promise<{
    protocol: string;
    version: number;
    supported_networks: string[];
    contract_version: string;
  }> => {
    const response = await api.get<{
      protocol: string;
      version: number;
      supported_networks: string[];
      contract_version: string;
    }>(`${API}/api/v1/blockchain/protocol`);
    return response;
  },
};
