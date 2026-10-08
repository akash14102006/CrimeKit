"use client";

import { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  ShieldCheck,
  ShieldAlert,
  Loader2,
  RefreshCw,
  FileCheck,
  Key,
  TreePine,
  Link2,
  Target,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useVerifyEvidence } from "../hooks/useBlockchain";
import { cn } from "@/lib/utils";

interface Props {
  evidenceId: string;
}

interface VerificationStep {
  label: string;
  description: string;
  passed: boolean | null;
  icon: React.ComponentType<{ className?: string }>;
}

export function VerificationReport({ evidenceId }: Props) {
  const verifyMutation = useVerifyEvidence(evidenceId);
  const [hasRun, setHasRun] = useState(false);

  const handleVerify = () => {
    setHasRun(true);
    verifyMutation.mutate();
  };

  const report = verifyMutation.data;

  const steps: VerificationStep[] = report
    ? [
        {
          label: "File Integrity",
          description: "SHA-256 hash matches the original upload",
          passed: report.evidence_hash_match,
          icon: FileCheck,
        },
        {
          label: "Commitment Validity",
          description: "Cryptographic commitment is valid",
          passed: report.commitment_valid,
          icon: Key,
        },
        {
          label: "Merkle Proof",
          description: "Merkle inclusion proof verified",
          passed: report.merkle_proof_valid,
          icon: TreePine,
        },
        {
          label: "Blockchain Anchor",
          description: "Transaction confirmed on-chain",
          passed: report.blockchain_confirmed,
          icon: Link2,
        },
        {
          label: "Overall Result",
          description: "All verification checks passed",
          passed: report.overall_result === "valid",
          icon: Target,
        },
      ]
    : [];

  const allPassed = steps.length > 0 && steps.every((s) => s.passed === true);
  const anyFailed = steps.some((s) => s.passed === false);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {allPassed ? (
              <ShieldCheck className="h-5 w-5 text-green-500" />
            ) : anyFailed ? (
              <ShieldAlert className="h-5 w-5 text-destructive" />
            ) : (
              <ShieldCheck className="h-5 w-5 text-muted-foreground" />
            )}
            Blockchain Verification
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={handleVerify}
            disabled={verifyMutation.isPending}
          >
            {verifyMutation.isPending ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <RefreshCw className="h-3.5 w-3.5" />
            )}
            {verifyMutation.isPending ? "Verifying..." : hasRun ? "Re-verify" : "Verify"}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {!hasRun ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <ShieldCheck className="h-12 w-12 text-muted-foreground/50 mb-3" />
            <p className="text-sm text-muted-foreground">
              Click &quot;Verify&quot; to run a full blockchain verification of this evidence.
            </p>
          </div>
        ) : verifyMutation.isPending ? (
          <div className="space-y-3">
            {["File Integrity", "Commitment Validity", "Merkle Proof", "Blockchain Anchor", "Overall Result"].map(
              (label) => (
                <div key={label} className="flex items-center gap-3">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                  <div className="flex-1">
                    <div className="h-4 w-32 rounded bg-muted animate-pulse" />
                    <div className="h-3 w-48 rounded bg-muted animate-pulse mt-1" />
                  </div>
                </div>
              )
            )}
          </div>
        ) : verifyMutation.isError ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <XCircle className="h-12 w-12 text-destructive mb-3" />
            <p className="text-sm font-medium text-destructive">Verification Failed</p>
            <p className="text-xs text-muted-foreground mt-1">
              Could not complete verification. Please try again.
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            {steps.map((step, index) => {
              const StepIcon = step.icon || ShieldCheck;
              return (
                <div
                  key={step.label}
                  className={cn(
                    "flex items-center gap-3 rounded-lg p-3 transition-colors",
                    step.passed === true && "bg-green-500/5",
                    step.passed === false && "bg-destructive/5",
                    step.passed === null && "bg-muted/50"
                  )}
                >
                  <div className="flex items-center justify-center">
                    {step.passed === true ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : step.passed === false ? (
                      <XCircle className="h-5 w-5 text-destructive" />
                    ) : (
                      <Loader2 className="h-5 w-5 text-muted-foreground animate-spin" />
                    )}
                  </div>
                  <StepIcon className="h-4 w-4 text-muted-foreground shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{step.label}</span>
                      <Badge
                        variant={step.passed === true ? "default" : step.passed === false ? "destructive" : "secondary"}
                        className="text-[10px]"
                      >
                        {step.passed === true ? "PASS" : step.passed === false ? "FAIL" : "PENDING"}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{step.description}</p>
                  </div>
                  {index < steps.length - 1 && (
                    <div className="absolute left-[29px] mt-8 h-2 w-px bg-border" />
                  )}
                </div>
              );
            })}

            {allPassed && (
              <div className="mt-4 rounded-lg border border-green-500/20 bg-green-500/5 p-3">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <span className="text-sm font-medium text-green-700 dark:text-green-400">
                    Evidence Verified Successfully
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  All cryptographic checks passed. This evidence is cryptographically proven to be authentic and unaltered.
                </p>
              </div>
            )}

            {anyFailed && (
              <div className="mt-4 rounded-lg border border-destructive/20 bg-destructive/5 p-3">
                <div className="flex items-center gap-2">
                  <XCircle className="h-4 w-4 text-destructive" />
                  <span className="text-sm font-medium text-destructive">
                    Verification Failed
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  One or more verification checks failed. This evidence may have been tampered with or is not properly anchored.
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
