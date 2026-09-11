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
  FileCheck,
  Plus,
  RefreshCw,
  Clock,
  Trash2,
  Edit,
  Loader2,
  AlertTriangle,
  Play,
} from "lucide-react";
import {
  useRetentionPolicies,
  useCreateRetentionPolicy,
  useDeleteRetentionPolicy,
  useExecuteRetention,
} from "../hooks/useCompliance";
import { toast } from "@/components/ui/toast";
import type { RetentionPolicy } from "@/types/compliance";

function PolicyCard({ policy }: { policy: RetentionPolicy }) {
  const deletePolicy = useDeleteRetentionPolicy();

  const handleDelete = useCallback(async () => {
    try {
      await deletePolicy.mutateAsync(policy.id);
      toast.add({ title: "Policy Deleted", description: `"${policy.name}" deleted.`, type: "success" });
    } catch {
      toast.add({ title: "Delete Failed", description: "Could not delete policy.", type: "error" });
    }
  }, [deletePolicy, policy.id, policy.name]);

  return (
    <div className="p-3 rounded-lg border hover:bg-muted/30 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Badge variant={policy.is_active ? "default" : "secondary"} className="text-[9px]">
            {policy.is_active ? "Active" : "Inactive"}
          </Badge>
          <span className="text-xs font-medium">{policy.name}</span>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-destructive" onClick={handleDelete} disabled={deletePolicy.isPending}>
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>
      <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
        <span>{policy.retention_days} days</span>
        {policy.evidence_type && <span>Type: {policy.evidence_type}</span>}
        {policy.classification && <span>Class: {policy.classification}</span>}
        <span>Action: {policy.action_on_expiry}</span>
      </div>
      {policy.legal_hold_override && (
        <Badge variant="outline" className="text-[8px] mt-1">Legal Hold Override</Badge>
      )}
    </div>
  );
}

export const RetentionPoliciesPanel = memo(function RetentionPoliciesPanel() {
  const { data, isLoading, refetch } = useRetentionPolicies();
  const createPolicy = useCreateRetentionPolicy();
  const executeRetention = useExecuteRetention();
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [name, setName] = useState("");
  const [retentionDays, setRetentionDays] = useState("365");
  const [evidenceType, setEvidenceType] = useState("");
  const [classification, setClassification] = useState("confidential");
  const policies = data?.policies ?? [];

  const handleCreate = useCallback(async () => {
    if (!name.trim()) return;
    try {
      await createPolicy.mutateAsync({
        name: name.trim(),
        retention_days: parseInt(retentionDays) || 365,
        evidence_type: evidenceType.trim() || undefined,
        classification: classification.trim() || undefined,
      });
      toast.add({ title: "Policy Created", description: `"${name}" created.`, type: "success" });
      setShowCreateDialog(false);
      setName("");
      setRetentionDays("365");
      setEvidenceType("");
      setClassification("confidential");
    } catch {
      toast.add({ title: "Create Failed", description: "Could not create policy.", type: "error" });
    }
  }, [name, retentionDays, evidenceType, classification, createPolicy]);

  const handleExecute = useCallback(async () => {
    try {
      const result = await executeRetention.mutateAsync();
      toast.add({ title: "Retention Executed", description: `${result.items_expired} items expired, ${result.items_deleted} deleted.`, type: "success" });
    } catch {
      toast.add({ title: "Execute Failed", description: "Could not execute retention.", type: "error" });
    }
  }, [executeRetention]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <FileCheck className="h-4 w-4" />
          Retention Policies
          {policies.length > 0 && <Badge variant="secondary" className="text-[10px]">{policies.length}</Badge>}
        </CardTitle>
        <div className="flex items-center gap-1">
          <Button variant="outline" size="sm" className="h-7 text-[10px] gap-1" onClick={handleExecute} disabled={executeRetention.isPending}>
            {executeRetention.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Play className="h-3 w-3" />}
            Execute
          </Button>
          <Button variant="outline" size="sm" className="h-7 text-[10px] gap-1" onClick={() => setShowCreateDialog(true)}>
            <Plus className="h-3 w-3" />
            New Policy
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
        ) : policies.length === 0 ? (
          <div className="text-center py-6">
            <FileCheck className="h-8 w-8 mx-auto text-muted-foreground/30 mb-2" />
            <p className="text-sm font-medium">No Retention Policies</p>
            <p className="text-xs text-muted-foreground">Create policies to manage evidence retention.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {policies.map((policy) => (
              <PolicyCard key={policy.id} policy={policy} />
            ))}
          </div>
        )}

        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <FileCheck className="h-4 w-4" />
                Create Retention Policy
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              <div className="space-y-2">
                <Label className="text-xs">Policy Name *</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Policy name" className="h-8 text-xs" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Retention Period (days)</Label>
                <Input value={retentionDays} onChange={(e) => setRetentionDays(e.target.value)} type="number" className="h-8 text-xs" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Evidence Type (optional)</Label>
                <Input value={evidenceType} onChange={(e) => setEvidenceType(e.target.value)} placeholder="e.g., image, video" className="h-8 text-xs" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Classification</Label>
                <Input value={classification} onChange={(e) => setClassification(e.target.value)} placeholder="confidential" className="h-8 text-xs" />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" size="sm" onClick={() => setShowCreateDialog(false)}>Cancel</Button>
              <Button size="sm" onClick={handleCreate} disabled={!name.trim() || createPolicy.isPending}>
                {createPolicy.isPending && <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />}
                Create Policy
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
});
