"use client";

import { useState } from "react";
import {
  Download,
  Copy,
  CheckCircle2,
  FileText,
  Link2,
  TreePine,
  Shield,
  Loader2,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useProofBundle } from "../hooks/useBlockchain";
import { toast } from "@/components/ui/toast";
import { cn } from "@/lib/utils";

interface Props {
  evidenceId: string;
  trigger?: React.ReactElement;
}

export function ProofBundleModal({ evidenceId, trigger }: Props) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const { data: proof, isLoading, error, refetch } = useProofBundle(open ? evidenceId : undefined);

  const handleCopy = async () => {
    if (!proof) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(proof, null, 2));
      setCopied(true);
      toast.add({
        title: "Copied",
        description: "Proof bundle copied to clipboard.",
        type: "success",
      });
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.add({
        title: "Copy Failed",
        description: "Could not copy to clipboard.",
        type: "error",
      });
    }
  };

  const handleDownload = () => {
    if (!proof) return;
    const blob = new Blob([JSON.stringify(proof, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `proof-bundle-${evidenceId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const sections = proof
    ? [
        {
          title: "Protocol",
          icon: Shield,
          items: [
            { label: "Protocol", value: proof.protocol },
            { label: "Version", value: String(proof.version) },
            { label: "Evidence ID", value: proof.evidence_id },
          ],
        },
        {
          title: "Evidence Hash",
          icon: FileText,
          items: [
            { label: "SHA-256", value: proof.evidence_sha256 },
            { label: "Commitment Hash", value: proof.commitment_hash },
          ],
        },
        {
          title: "Merkle Proof",
          icon: TreePine,
          items: [
            { label: "Leaf Index", value: String(proof.merkle_proof.leaf_index) },
            { label: "Root", value: proof.merkle_proof.root },
            { label: "Siblings", value: `${proof.merkle_proof.siblings.length} levels` },
          ],
        },
        {
          title: "Blockchain",
          icon: Link2,
          items: [
            { label: "Network", value: proof.blockchain.network },
            { label: "Chain ID", value: String(proof.blockchain.chain_id) },
            { label: "Contract", value: proof.blockchain.contract_address },
            { label: "Tx Hash", value: proof.blockchain.tx_hash },
            { label: "Block", value: `#${proof.blockchain.block_number.toLocaleString()}` },
            { label: "Timestamp", value: new Date(proof.blockchain.timestamp).toLocaleString() },
          ],
        },
      ]
    : [];

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          trigger ??
          <Button variant="outline" size="sm" className="gap-1">
            <FileText className="h-3.5 w-3.5" />
            View Proof
          </Button>
        }
      />
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Proof Bundle
          </DialogTitle>
          <DialogDescription>
            Cryptographic proof bundle for evidence integrity verification.
          </DialogDescription>
        </DialogHeader>

        <div className="max-h-[60vh] overflow-y-auto">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="space-y-2">
                  <div className="h-4 w-24 rounded bg-muted animate-pulse" />
                  <div className="h-3 w-full rounded bg-muted animate-pulse" />
                  <div className="h-3 w-3/4 rounded bg-muted animate-pulse" />
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <p className="text-sm text-muted-foreground">
                No proof bundle available for this evidence.
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-3"
                onClick={() => refetch()}
              >
                Retry
              </Button>
            </div>
          ) : proof ? (
            <div className="space-y-4">
              {sections.map((section) => {
                const SectionIcon = section.icon;
                return (
                  <div key={section.title} className="rounded-lg border p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <SectionIcon className="h-4 w-4 text-muted-foreground" />
                      <h4 className="text-sm font-medium">{section.title}</h4>
                    </div>
                    <div className="space-y-1.5">
                      {section.items.map((item) => (
                        <div key={item.label} className="flex items-start justify-between gap-2">
                          <span className="text-xs text-muted-foreground shrink-0">{item.label}</span>
                          <span className="text-xs font-mono text-right break-all">{item.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}

              {proof.merkle_proof.siblings.length > 0 && (
                <div className="rounded-lg border p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <TreePine className="h-4 w-4 text-muted-foreground" />
                    <h4 className="text-sm font-medium">Merkle Siblings</h4>
                  </div>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {proof.merkle_proof.siblings.map((sibling, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-[10px] w-8 justify-center">
                          L{index}
                        </Badge>
                        <span className="text-[11px] font-mono text-muted-foreground break-all">
                          {sibling}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Close
          </Button>
          {proof && (
            <>
              <Button variant="outline" onClick={handleCopy}>
                {copied ? (
                  <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                ) : (
                  <Copy className="h-3.5 w-3.5" />
                )}
                {copied ? "Copied" : "Copy JSON"}
              </Button>
              <Button onClick={handleDownload}>
                <Download className="h-3.5 w-3.5" />
                Download JSON
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
