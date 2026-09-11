"use client";

import { useState } from "react";
import { Trash2, FolderInput, Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useReassignEvidence } from "@/hooks/queries/useEvidence";
import { useCases } from "@/hooks/queries/useCases";
import { evidenceService } from "@/services/evidenceService";
import { exportEvidenceToCSV } from "../lib/export";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";
import { useRBAC } from "@/hooks/useRBAC";
import type { Evidence } from "@/types/evidence";

interface BulkActionsProps {
  selectedItems: Evidence[];
  onClearSelection: () => void;
  onRefresh: () => void;
}

export function BulkActions({ selectedItems, onClearSelection, onRefresh }: BulkActionsProps) {
  const { hasPermission } = useRBAC();
  const canDelete = hasPermission("evidence:delete");
  const canReassign = hasPermission("case:update");
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [reassignOpen, setReassignOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const count = selectedItems.length;
  if (count === 0) return null;

  const handleBulkDelete = async () => {
    setDeleting(true);
    let successCount = 0;
    let failCount = 0;
    for (const item of selectedItems) {
      try {
        await evidenceService.delete(item.id);
        successCount++;
      } catch {
        failCount++;
      }
    }
    setDeleting(false);
    setDeleteOpen(false);
    toast.add({
      title: "Bulk Delete Complete",
      description: `${successCount} deleted${failCount > 0 ? `, ${failCount} failed` : ""}.`,
      type: successCount > 0 ? "success" : "error",
    });
    onClearSelection();
    onRefresh();
  };

  const handleExportCSV = () => {
    exportEvidenceToCSV(selectedItems, `evidence-${count}-items.csv`);
    toast.add({
      title: "Export Complete",
      description: `${count} evidence items exported to CSV.`,
      type: "success",
    });
  };

  return (
    <>
      <div className="flex items-center gap-2 p-3 rounded-md border bg-muted/50">
        <span className="text-sm font-medium">{count} selected</span>
        <div className="flex-1" />
        <Button variant="outline" size="sm" className="gap-1" onClick={handleExportCSV}>
          <Download className="h-3.5 w-3.5" />
          Export CSV
        </Button>
        {canReassign && (
          <Button variant="outline" size="sm" className="gap-1" onClick={() => setReassignOpen(true)}>
            <FolderInput className="h-3.5 w-3.5" />
            Reassign
          </Button>
        )}
        {canDelete && (
          <Button variant="destructive" size="sm" className="gap-1" onClick={() => setDeleteOpen(true)}>
            <Trash2 className="h-3.5 w-3.5" />
            Delete
          </Button>
        )}
        <Button variant="ghost" size="sm" onClick={onClearSelection}>
          Clear
        </Button>
      </div>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Delete {count} Evidence Items</DialogTitle>
            <DialogDescription>
              Are you sure you want to permanently delete {count} evidence items?
              Chain of custody and audit history will be preserved.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleBulkDelete}
              disabled={deleting}
            >
              {deleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                `Delete ${count} Items`
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {reassignOpen && (
        <BulkReassignDialog
          open={reassignOpen}
          onOpenChange={setReassignOpen}
          selectedItems={selectedItems}
          onDone={() => {
            onClearSelection();
            onRefresh();
          }}
        />
      )}
    </>
  );
}

function BulkReassignDialog({
  open,
  onOpenChange,
  selectedItems,
  onDone,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  selectedItems: Evidence[];
  onDone: () => void;
}) {
  const [caseId, setCaseId] = useState("");
  const reassignEvidence = useReassignEvidence();
  const { data: casesData } = useCases({ page: 1, limit: 100 });
  const cases = casesData?.items ?? [];

  const handleReassign = async () => {
    let successCount = 0;
    for (const item of selectedItems) {
      try {
        await reassignEvidence.mutateAsync({
          evidenceId: item.id,
          caseId: caseId || null,
        });
        successCount++;
      } catch {
        // continue
      }
    }
    toast.add({
      title: "Bulk Reassign Complete",
      description: `${successCount} of ${selectedItems.length} items reassigned.`,
      type: "success",
    });
    onOpenChange(false);
    onDone();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Reassign {selectedItems.length} Items</DialogTitle>
          <DialogDescription>
            Select a case to reassign the selected evidence items to.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <select
            value={caseId}
            onChange={(e) => setCaseId(e.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
          >
            <option value="">Unassign (no case)</option>
            {cases.map((c) => (
              <option key={c.id} value={c.id}>
                {c.title}
              </option>
            ))}
          </select>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleReassign} disabled={reassignEvidence.isPending}>
            {reassignEvidence.isPending ? "Reassigning..." : "Reassign"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
