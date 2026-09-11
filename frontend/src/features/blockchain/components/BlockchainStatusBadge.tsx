"use client";

import { useState } from "react";
import {
  Link2,
  Loader2,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Clock,
  ChevronDown,
  ChevronUp,
  Copy,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useBlockchainStatus } from "../hooks/useBlockchain";
import { cn } from "@/lib/utils";

interface Props {
  proofId?: string;
  evidenceId: string;
  status?: string;
  size?: "sm" | "md";
}

export function BlockchainStatusBadge({ proofId, evidenceId, status: overrideStatus, size = "sm" }: Props) {
  const { data: anchor, isLoading } = useBlockchainStatus(evidenceId, overrideStatus ? undefined : 5000);
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const effectiveStatus = overrideStatus || anchor?.status;

  const getStatusConfig = (s?: string) => {
    switch (s) {
      case "anchored":
        return {
          label: "Anchored",
          variant: "default" as const,
          icon: CheckCircle2,
          color: "text-green-500",
          bgColor: "bg-green-500/10",
        };
      case "anchoring":
        return {
          label: "Anchoring",
          variant: "secondary" as const,
          icon: Loader2,
          color: "text-amber-500",
          bgColor: "bg-amber-500/10",
        };
      case "failed":
        return {
          label: "Failed",
          variant: "destructive" as const,
          icon: XCircle,
          color: "text-destructive",
          bgColor: "bg-destructive/10",
        };
      default:
        return {
          label: "Not Anchored",
          variant: "outline" as const,
          icon: Clock,
          color: "text-muted-foreground",
          bgColor: "bg-muted",
        };
    }
  };

  const config = getStatusConfig(effectiveStatus);
  const Icon = config.icon;

  const handleCopyTxHash = async () => {
    if (!anchor?.tx_hash) return;
    try {
      await navigator.clipboard.writeText(anchor.tx_hash);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API not available
    }
  };

  const getExplorerUrl = () => {
    if (!anchor?.tx_hash) return null;
    const network = anchor.network;
    if (network === "ethereum" || network === "sepolia") {
      return `https://sepolia.etherscan.io/tx/${anchor.tx_hash}`;
    }
    if (network === "polygon") {
      return `https://polygonscan.com/tx/${anchor.tx_hash}`;
    }
    return null;
  };

  const explorerUrl = getExplorerUrl();

  if (isLoading) {
    return (
      <div
        className={cn(
          "inline-flex items-center gap-1 rounded-full border border-transparent px-2 py-0.5 text-xs font-medium",
          size === "sm" ? "h-5" : "h-6",
          "bg-muted text-muted-foreground"
        )}
      >
        <Loader2 className="h-3 w-3 animate-spin" />
        <span>Checking...</span>
      </div>
    );
  }

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className={cn(
          "inline-flex items-center gap-1 rounded-full border border-transparent px-2 py-0.5 text-xs font-medium transition-colors",
          size === "sm" ? "h-5" : "h-6",
          config.bgColor,
          "hover:opacity-80 cursor-pointer"
        )}
      >
        <Icon className={cn("h-3 w-3", config.color, effectiveStatus === "anchoring" && "animate-spin")} />
        <span className={config.color}>{config.label}</span>
        {anchor && (
          expanded ? (
            <ChevronUp className="h-3 w-3 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-3 w-3 text-muted-foreground" />
          )
        )}
      </button>

      {expanded && anchor && (
        <div className="absolute z-50 mt-2 w-80 rounded-xl border bg-popover p-3 shadow-lg">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Status</span>
              <Badge variant={effectiveStatus === "anchored" ? "default" : effectiveStatus === "failed" ? "destructive" : "secondary"}>
                {effectiveStatus}
              </Badge>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Network</span>
              <span className="text-xs font-mono">{anchor.network}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Merkle Root</span>
              <span className="text-xs font-mono truncate max-w-[160px]">{anchor.merkle_root}</span>
            </div>

            {anchor.tx_hash && (
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-muted-foreground shrink-0">Tx Hash</span>
                <div className="flex items-center gap-1">
                  <span className="text-xs font-mono truncate max-w-[140px]">
                    {anchor.tx_hash.slice(0, 10)}...{anchor.tx_hash.slice(-6)}
                  </span>
                  <button
                    type="button"
                    onClick={handleCopyTxHash}
                    className="text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {copied ? (
                      <CheckCircle2 className="h-3 w-3 text-green-500" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </button>
                  {explorerUrl && (
                    <a
                      href={explorerUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-muted-foreground hover:text-foreground transition-colors"
                    >
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
              </div>
            )}

            {anchor.block_number && (
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground">Block</span>
                <span className="text-xs font-mono">#{anchor.block_number.toLocaleString()}</span>
              </div>
            )}

            {anchor.contract_address && (
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-muted-foreground shrink-0">Contract</span>
                <span className="text-xs font-mono truncate max-w-[160px]">
                  {anchor.contract_address.slice(0, 10)}...{anchor.contract_address.slice(-6)}
                </span>
              </div>
            )}

            {anchor.anchored_at && (
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground">Anchored At</span>
                <span className="text-xs">
                  {new Date(anchor.anchored_at).toLocaleString()}
                </span>
              </div>
            )}

            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-muted-foreground">Created</span>
              <span className="text-xs">
                {new Date(anchor.created_at).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
