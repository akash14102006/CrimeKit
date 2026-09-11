"use client";

import { Copy } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "@/components/ui/toast";
import type { Evidence } from "@/types/evidence";

interface Props {
  evidence: Evidence | undefined;
  isLoading: boolean;
}

export function EvidenceHashCard({ evidence, isLoading }: Props) {
  const copyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    toast.add({ title: "Copied", description: "Hash copied to clipboard.", type: "success" });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>File Hash (SHA-256)</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-start gap-2">
              <code className="flex-1 text-xs font-mono bg-muted p-3 rounded-md break-all leading-relaxed">
                {evidence?.sha256 ?? "N/A"}
              </code>
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={() => evidence?.sha256 && copyHash(evidence.sha256)}
                aria-label="Copy SHA-256 hash"
                className="shrink-0 mt-1"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Content-addressable SHA-256 hash computed at upload time. Used for integrity verification.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
