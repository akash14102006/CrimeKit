"use client";

import { ShieldCheck, ShieldAlert } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useEvidenceCustody } from "@/hooks/queries/useEvidence";

interface Props {
  evidenceId: string;
}

export function EvidenceIntegrityCard({ evidenceId }: Props) {
  const { data: custody, isLoading } = useEvidenceCustody(evidenceId);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Integrity Status</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-6 w-[120px]" />
            <Skeleton className="h-4 w-[200px]" />
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              {custody?.integrity_ok ? (
                <ShieldCheck className="h-8 w-8 text-green-500" />
              ) : (
                <ShieldAlert className="h-8 w-8 text-destructive" />
              )}
              <div>
                <Badge variant={custody?.integrity_ok ? "default" : "destructive"}>
                  {custody?.integrity_ok ? "Integrity Verified" : "Integrity Compromised"}
                </Badge>
                <p className="text-xs text-muted-foreground mt-1">
                  {custody?.integrity_ok
                    ? "File SHA-256 matches the original upload hash."
                    : "File has been modified since upload. Possible tampering detected."}
                </p>
              </div>
            </div>
            <div className="text-xs text-muted-foreground">
              Chain of Custody entries: {custody?.history?.length ?? 0}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
