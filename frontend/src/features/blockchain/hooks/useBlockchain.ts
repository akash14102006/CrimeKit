import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  blockchainService,
  type AnchorRecord,
  type VerificationReport,
  type ProofBundle,
  type BlockchainStats,
} from "../services/blockchainService";

export function useBlockchainStatus(evidenceId?: string, pollingInterval = 5000) {
  return useQuery<AnchorRecord | null>({
    queryKey: ["blockchain", "status", evidenceId],
    queryFn: async () => {
      if (!evidenceId) return null;
      try {
        const result = await blockchainService.getAnchor(evidenceId);
        return result;
      } catch {
        return null;
      }
    },
    enabled: !!evidenceId,
    refetchInterval: pollingInterval,
  });
}

export function useVerification(evidenceId?: string) {
  const queryClient = useQueryClient();
  return useQuery<VerificationReport | null>({
    queryKey: ["blockchain", "verification", evidenceId],
    queryFn: async () => {
      if (!evidenceId) return null;
      return blockchainService.verifyEvidence(evidenceId);
    },
    enabled: false,
    retry: false,
  });
}

export function useVerifyEvidence(evidenceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => blockchainService.verifyEvidence(evidenceId),
    onSuccess: () => {
      queryClient.setQueryData(
        ["blockchain", "verification", evidenceId],
        (old: VerificationReport | undefined) => old
      );
    },
  });
}

export function useProofBundle(evidenceId?: string) {
  return useQuery<ProofBundle>({
    queryKey: ["blockchain", "proof", evidenceId],
    queryFn: () => blockchainService.getProofBundle(evidenceId as string),
    enabled: !!evidenceId,
    retry: false,
  });
}

export function useBlockchainStats() {
  return useQuery<BlockchainStats>({
    queryKey: ["blockchain", "stats"],
    queryFn: () => blockchainService.getStats(),
    refetchInterval: 30000,
  });
}

export function useAnchorEvidence() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (evidenceId: string) => blockchainService.anchorEvidence(evidenceId),
    onSuccess: (_data, evidenceId) => {
      queryClient.invalidateQueries({ queryKey: ["blockchain", "status", evidenceId] });
      queryClient.invalidateQueries({ queryKey: ["blockchain", "stats"] });
      queryClient.invalidateQueries({ queryKey: ["blockchain", "batches"] });
    },
  });
}

export function useAnchorBatch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => blockchainService.anchorBatch(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["blockchain", "stats"] });
      queryClient.invalidateQueries({ queryKey: ["blockchain", "batches"] });
    },
  });
}

export function useMerkleBatches() {
  return useQuery({
    queryKey: ["blockchain", "batches"],
    queryFn: () => blockchainService.getMerkleBatches(),
  });
}

export function useProvenance(evidenceId?: string) {
  return useQuery({
    queryKey: ["blockchain", "provenance", evidenceId],
    queryFn: () => blockchainService.getProvenance(evidenceId as string),
    enabled: !!evidenceId,
  });
}

export function useBlockchainProtocol() {
  return useQuery({
    queryKey: ["blockchain", "protocol"],
    queryFn: () => blockchainService.getProtocol(),
  });
}
