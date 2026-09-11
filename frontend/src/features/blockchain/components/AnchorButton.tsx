"use client";

import { useState } from "react";
import { Link2, Loader2, CheckCircle2, XCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useAnchorEvidence } from "../hooks/useBlockchain";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";
import { cn } from "@/lib/utils";

interface Props {
  evidenceId: string;
  onAnchored?: () => void;
}

export function AnchorButton({ evidenceId, onAnchored }: Props) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const anchorMutation = useAnchorEvidence();

  const handleAnchor = async () => {
    try {
      await anchorMutation.mutateAsync(evidenceId);
      toast.add({
        title: "Evidence Anchored",
        description: "Evidence has been successfully anchored to the blockchain.",
        type: "success",
      });
      setConfirmOpen(false);
      onAnchored?.();
    } catch (error) {
      toast.add({
        title: "Anchoring Failed",
        description: getErrorMessage(error, "Could not anchor evidence to blockchain."),
        type: "error",
      });
    }
  };

  const isSuccess = anchorMutation.isSuccess;
  const isError = anchorMutation.isError;
  const isPending = anchorMutation.isPending;

  return (
    <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
      <DialogTrigger
        render={
          <Button
            variant={isSuccess ? "outline" : "default"}
            size="sm"
            className={cn(
              "gap-1.5",
              isSuccess && "border-green-500/20 text-green-600 dark:text-green-400",
              isError && "border-destructive/20"
            )}
          />
        }
      >
        {isSuccess ? (
          <>
            <CheckCircle2 className="h-3.5 w-3.5" />
            Anchored
          </>
        ) : isError ? (
          <>
            <RefreshCw className="h-3.5 w-3.5" />
            Retry Anchor
          </>
        ) : (
          <>
            <Link2 className="h-3.5 w-3.5" />
            Anchor to Blockchain
          </>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Link2 className="h-5 w-5" />
            Anchor to Blockchain
          </DialogTitle>
          <DialogDescription>
            This will create a cryptographic commitment and anchor it to the blockchain.
            This action is irreversible.
          </DialogDescription>
        </DialogHeader>
        <div className="rounded-lg border bg-muted/50 p-3">
          <p className="text-xs text-muted-foreground">
            A SHA-256 hash of the evidence will be embedded in a Merkle tree and
            anchored to the blockchain, creating a tamper-proof record of this
            evidence&apos;s existence and integrity at this point in time.
          </p>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setConfirmOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleAnchor} disabled={isPending}>
            {isPending ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Anchoring...
              </>
            ) : (
              <>
                <Link2 className="h-3.5 w-3.5" />
                Confirm Anchor
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
