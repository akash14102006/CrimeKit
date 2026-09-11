"use client";

import { memo, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Scale,
  Loader2,
  AlertTriangle,
  Clock,
  User,
  CheckCircle2,
  XCircle,
  Plus,
} from "lucide-react";
import { useGDPRStatus, useInitiateGDPRDeletion } from "../hooks/useCompliance";
import { toast } from "@/components/ui/toast";

export const GDPRRequestsPanel = memo(function GDPRRequestsPanel() {
  const [showInitDialog, setShowInitDialog] = useState(false);
  const [userId, setUserId] = useState("");
  const [reason, setReason] = useState("");
  const initiateDeletion = useInitiateGDPRDeletion();

  const handleInitiate = useCallback(async () => {
    if (!userId.trim()) return;
    try {
      await initiateDeletion.mutateAsync({ userId: userId.trim(), reason: reason.trim() || undefined });
      toast.add({ title: "GDPR Request Initiated", description: `Deletion request for user ${userId} submitted.`, type: "success" });
      setShowInitDialog(false);
      setUserId("");
      setReason("");
    } catch {
      toast.add({ title: "Failed", description: "Could not initiate GDPR request.", type: "error" });
    }
  }, [userId, reason, initiateDeletion]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Scale className="h-4 w-4" />
          GDPR Requests
        </CardTitle>
        <Button variant="outline" size="sm" className="h-7 text-[10px] gap-1" onClick={() => setShowInitDialog(true)}>
          <Plus className="h-3 w-3" />
          New Request
        </Button>
      </CardHeader>
      <CardContent>
        <div className="text-center py-6">
          <Scale className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
          <p className="text-sm font-medium">GDPR Request Management</p>
          <p className="text-xs text-muted-foreground max-w-xs mx-auto">
            GDPR deletion and data subject requests are processed by the backend.
            Use the button above to initiate a new request.
          </p>
        </div>

        <Dialog open={showInitDialog} onOpenChange={setShowInitDialog}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Scale className="h-4 w-4" />
                Initiate GDPR Request
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              <div className="space-y-2">
                <Label className="text-xs">User ID *</Label>
                <Input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="Enter user ID" className="h-8 text-xs" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Reason (optional)</Label>
                <Input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Reason for deletion..." className="h-8 text-xs" />
              </div>
              <div className="flex items-center gap-2 p-2 rounded bg-amber-50 border border-amber-200">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-600 shrink-0" />
                <p className="text-[10px] text-amber-700">
                  This will initiate a GDPR right-to-deletion request. The backend will process anonymization across all relevant tables.
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" size="sm" onClick={() => setShowInitDialog(false)}>Cancel</Button>
              <Button size="sm" onClick={handleInitiate} disabled={!userId.trim() || initiateDeletion.isPending}>
                {initiateDeletion.isPending && <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />}
                Submit Request
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
});
