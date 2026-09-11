"use client";

import { memo, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Lock,
  Unlock,
  Plus,
  RefreshCw,
  Clock,
  User,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import { useLegalHolds, usePlaceLegalHold, useReleaseLegalHold } from "../hooks/useCompliance";
import { useComplianceStore } from "../store/complianceStore";
import { toast } from "@/components/ui/toast";
import type { LegalHold } from "@/types/compliance";

const STATUS_CONFIG: Record<string, { color: string; icon: React.ReactNode }> = {
  active: { color: "bg-amber-100 text-amber-700", icon: <Lock className="h-3 w-3" /> },
  released: { color: "bg-emerald-100 text-emerald-700", icon: <Unlock className="h-3 w-3" /> },
};

function HoldCard({ hold }: { hold: LegalHold }) {
  const releaseHold = useReleaseLegalHold();
  const config = STATUS_CONFIG[hold.status] || STATUS_CONFIG.active;

  const handleRelease = useCallback(async () => {
    try {
      await releaseHold.mutateAsync(hold.id);
      toast.add({ title: "Hold Released", description: `Legal hold ${hold.id.slice(0, 8)} released.`, type: "success" });
    } catch {
      toast.add({ title: "Release Failed", description: "Could not release the legal hold.", type: "error" });
    }
  }, [releaseHold, hold.id]);

  return (
    <div className="p-3 rounded-lg border hover:bg-muted/30 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Badge className={`text-[9px] ${config.color}`}>
            {config.icon}
            {hold.status}
          </Badge>
          <span className="text-xs font-mono">{hold.id.slice(0, 8)}</span>
        </div>
        {hold.status === "active" && (
          <Button variant="ghost" size="sm" className="h-6 text-[10px] gap-1 text-destructive" onClick={handleRelease} disabled={releaseHold.isPending}>
            {releaseHold.isPending ? <Loader2 className="h-2.5 w-2.5 animate-spin" /> : <Unlock className="h-2.5 w-2.5" />}
            Release
          </Button>
        )}
      </div>
      <p className="text-xs mb-1">{hold.reason}</p>
      <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
        {hold.case_id && <span>Case: {hold.case_id.slice(0, 8)}</span>}
        {hold.evidence_id && <span>Evidence: {hold.evidence_id.slice(0, 8)}</span>}
        {hold.placed_by && <span className="flex items-center gap-0.5"><User className="h-2.5 w-2.5" />{hold.placed_by}</span>}
        {hold.placed_at && <span className="flex items-center gap-0.5"><Clock className="h-2.5 w-2.5" />{new Date(hold.placed_at).toLocaleDateString()}</span>}
      </div>
    </div>
  );
}

export const LegalHoldPanel = memo(function LegalHoldPanel() {
  const { data, isLoading, refetch } = useLegalHolds();
  const [showPlaceDialog, setShowPlaceDialog] = useState(false);
  const [caseId, setCaseId] = useState("");
  const [evidenceId, setEvidenceId] = useState("");
  const [reason, setReason] = useState("");
  const placeHold = usePlaceLegalHold();
  const holds = data?.holds ?? [];

  const handlePlace = useCallback(async () => {
    if (!reason.trim()) return;
    try {
      await placeHold.mutateAsync({
        case_id: caseId.trim() || undefined,
        evidence_id: evidenceId.trim() || undefined,
        reason: reason.trim(),
      });
      toast.add({ title: "Legal Hold Placed", description: "Legal hold has been placed successfully.", type: "success" });
      setShowPlaceDialog(false);
      setCaseId("");
      setEvidenceId("");
      setReason("");
    } catch {
      toast.add({ title: "Failed", description: "Could not place legal hold.", type: "error" });
    }
  }, [caseId, evidenceId, reason, placeHold]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Lock className="h-4 w-4" />
          Legal Holds
          {holds.length > 0 && <Badge variant="secondary" className="text-[10px]">{holds.length}</Badge>}
        </CardTitle>
        <div className="flex items-center gap-1">
          <Button variant="outline" size="sm" className="h-7 text-[10px] gap-1" onClick={() => setShowPlaceDialog(true)}>
            <Plus className="h-3 w-3" />
            Place Hold
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => refetch()}>
            <RefreshCw className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="p-3 border rounded-lg space-y-2">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-2 w-full" />
              </div>
            ))}
          </div>
        ) : holds.length === 0 ? (
          <div className="text-center py-6">
            <Lock className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
            <p className="text-sm font-medium">No Legal Holds</p>
            <p className="text-xs text-muted-foreground">No active legal holds on cases or evidence.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {holds.map((hold) => (
              <HoldCard key={hold.id} hold={hold} />
            ))}
          </div>
        )}

        <Dialog open={showPlaceDialog} onOpenChange={setShowPlaceDialog}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Lock className="h-4 w-4" />
                Place Legal Hold
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              <div className="space-y-2">
                <Label className="text-xs">Case ID (optional)</Label>
                <Input value={caseId} onChange={(e) => setCaseId(e.target.value)} placeholder="Case ID" className="h-8 text-xs" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Evidence ID (optional)</Label>
                <Input value={evidenceId} onChange={(e) => setEvidenceId(e.target.value)} placeholder="Evidence ID" className="h-8 text-xs" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Reason *</Label>
                <Input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Reason for legal hold..." className="h-8 text-xs" />
              </div>
              <div className="flex items-center gap-2 p-2 rounded bg-amber-50 border border-amber-200">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-600 shrink-0" />
                <p className="text-[10px] text-amber-700">
                  Legal holds prevent evidence deletion and retention expiry. This action will be logged in the audit trail.
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" size="sm" onClick={() => setShowPlaceDialog(false)}>Cancel</Button>
              <Button size="sm" onClick={handlePlace} disabled={!reason.trim() || placeHold.isPending}>
                {placeHold.isPending && <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />}
                Place Hold
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
});
