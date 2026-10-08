"use client";

import { useState } from "react";
import { Trash2, AlertTriangle } from "lucide-react";
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
import { useDeleteCase } from "@/hooks/queries/useCases";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";
import type { CaseOut } from "@/types/case";

interface DeleteCaseDialogProps {
  caseItem: CaseOut;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function DeleteCaseDialog({ caseItem, open: controlledOpen, onOpenChange: controlledOnOpenChange }: DeleteCaseDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen ?? internalOpen;
  const setOpen = controlledOnOpenChange ?? setInternalOpen;
  const deleteCase = useDeleteCase();

  const handleDelete = async () => {
    try {
      await deleteCase.mutateAsync(caseItem.id);
      toast.add({
        title: "Case Permanently Deleted",
        description: `Case "${caseItem.title}" and its associated records have been purged.`,
        type: "success",
      });
      setOpen(false);
    } catch (error) {
      toast.add({
        title: "Failed to Delete Case",
        description: getErrorMessage(error, "Could not delete the case."),
        type: "error",
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <button
            className="w-8 h-8 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 hover:bg-rose-500/25 hover:border-rose-500/40 transition-all"
            title="Delete Case File"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        }
      />
      <DialogContent className="sm:max-w-md p-6 bg-card border border-border rounded-xl shadow-xl text-card-foreground">
        <DialogHeader className="space-y-3">
          <div className="w-12 h-12 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-500">
            <AlertTriangle className="h-6 w-6" />
          </div>
          <div>
            <DialogTitle className="text-xl font-bold text-foreground">
              Purge Case File?
            </DialogTitle>
            <DialogDescription className="text-xs text-muted-foreground mt-1 leading-relaxed">
              Are you sure you want to permanently delete &quot;
              <span className="text-foreground font-semibold">{caseItem.title}</span>&quot;? This operation cannot be undone. All forensic evidence, correlates, and logs will be permanently erased.
            </DialogDescription>
          </div>
        </DialogHeader>

        <DialogFooter className="pt-4 border-t border-border flex items-center justify-end gap-3 mt-4">
          <Button
            variant="outline"
            onClick={() => setOpen(false)}
            className="h-9 px-4 rounded-lg border-border bg-card text-foreground hover:bg-muted"
          >
            Cancel
          </Button>
          <Button
            onClick={handleDelete}
            disabled={deleteCase.isPending}
            className="h-9 px-5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium transition-colors"
          >
            {deleteCase.isPending ? "Purging Case..." : "Delete Case File"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
