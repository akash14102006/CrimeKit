"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import { Download, Trash2, FolderInput, Loader2, Search, Check, Copy, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useDeleteEvidence, useReassignEvidence } from "@/hooks/queries/useEvidence";
import { useCases } from "@/hooks/queries/useCases";
import { evidenceService } from "@/services/evidenceService";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";
import { useRBAC } from "@/hooks/useRBAC";
import { useRouter } from "next/navigation";
import type { Evidence } from "@/types/evidence";
import { OpenDiskAnalyzerAction } from "./OpenDiskAnalyzerAction";

interface Props {
  evidence: Evidence;
}

export function EvidenceActions({ evidence }: Props) {
  const { hasPermission } = useRBAC();
  const canDelete = hasPermission("evidence:delete");
  const canReassign = hasPermission("case:update");
  const [downloading, setDownloading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      await evidenceService.download(evidence.id, evidence.filename);
    } catch (error) {
      toast.add({
        title: "Download Failed",
        description: getErrorMessage(error, "Could not download evidence file."),
        type: "error",
      });
    } finally {
      setDownloading(false);
    }
  };

  const handleCopyHash = async () => {
    const hash = evidence.sha256;
    if (!hash) {
      toast.add({ title: "No Hash", description: "No hash available to copy.", type: "error" });
      return;
    }
    try {
      await navigator.clipboard.writeText(hash);
      setCopied(true);
      toast.add({ title: "Copied", description: "SHA-256 hash copied to clipboard.", type: "success" });
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.add({ title: "Copy Failed", description: "Could not copy hash.", type: "error" });
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Button
        variant="outline"
        size="sm"
        className="gap-1"
        onClick={handleDownload}
        disabled={downloading}
      >
        {downloading ? (
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
        ) : (
          <Download className="h-3.5 w-3.5" />
        )}
        {downloading ? "Downloading..." : "Download"}
      </Button>
      <Button variant="outline" size="sm" className="gap-1" onClick={handleCopyHash}>
        {copied ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
        {copied ? "Copied" : "Copy Hash"}
      </Button>
      <OpenDiskAnalyzerAction evidence={evidence} />
      {canReassign && <ReassignEvidenceDialog evidence={evidence} />}
      {canDelete && <DeleteEvidenceDialog evidence={evidence} />}
    </div>
  );
}

function ReassignEvidenceDialog({ evidence }: { evidence: Evidence }) {
  const [open, setOpen] = useState(false);
  const [caseId, setCaseId] = useState(evidence.case_id || "");
  const [search, setSearch] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const reassignEvidence = useReassignEvidence();
  const { data: casesData, isLoading: casesLoading } = useCases({ page: 1, limit: 100 });

  useEffect(() => {
    if (!showDropdown) return;
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showDropdown]);

  const cases = useMemo(() => casesData?.items ?? [], [casesData]);
  const filteredCases = useMemo(() => {
    const q = search.toLowerCase();
    return cases.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.id.toLowerCase().includes(q),
    );
  }, [cases, search]);

  const selectedCase = useMemo(
    () => cases.find((c) => c.id === caseId),
    [cases, caseId],
  );

  const handleReassign = async () => {
    try {
      await reassignEvidence.mutateAsync({
        evidenceId: evidence.id,
        caseId: caseId || null,
      });
      toast.add({
        title: "Evidence Reassigned",
        description: `"${evidence.filename}" has been reassigned.`,
        type: "success",
      });
      setOpen(false);
    } catch (error) {
      toast.add({
        title: "Reassign Failed",
        description: getErrorMessage(error, "Could not reassign evidence."),
        type: "error",
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button variant="outline" size="sm" className="gap-1" />}>
        <FolderInput className="h-3.5 w-3.5" />
        Reassign
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Reassign Evidence</DialogTitle>
          <DialogDescription>
            Move this evidence to a different case. Leave empty to unassign.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Label htmlFor="reassign-case-search">Case</Label>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              id="reassign-case-search"
              value={showDropdown ? search : selectedCase?.title ?? search}
              onChange={(e) => {
                setSearch(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => {
                setShowDropdown(true);
                setSearch("");
              }}
              placeholder="Search cases by title or ID..."
              className="pl-8"
            />
            {showDropdown && (
              <div ref={dropdownRef} className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md max-h-48 overflow-y-auto">
                {casesLoading ? (
                  <div className="p-2 text-sm text-muted-foreground">Loading cases...</div>
                ) : filteredCases.length === 0 ? (
                  <div className="p-2 text-sm text-muted-foreground">No cases found</div>
                ) : (
                  filteredCases.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      className={`flex w-full items-center gap-2 px-2 py-1.5 text-sm hover:bg-accent ${
                        c.id === caseId ? "bg-accent" : ""
                      }`}
                      onClick={() => {
                        setCaseId(c.id);
                        setSearch("");
                        setShowDropdown(false);
                      }}
                    >
                      <Check
                        className={`h-3.5 w-3.5 shrink-0 ${
                          c.id === caseId ? "opacity-100" : "opacity-0"
                        }`}
                      />
                      <span className="truncate font-medium">{c.title}</span>
                      <span className="ml-auto text-xs text-muted-foreground font-mono shrink-0">
                        {c.id.split("-")[0]}
                      </span>
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
          {caseId && selectedCase && (
            <p className="text-xs text-muted-foreground">
              Selected: {selectedCase.title}
            </p>
          )}
          {evidence.case_id && (
            <p className="text-xs text-muted-foreground">
              Currently assigned to: {evidence.case_id.split("-")[0]}...
            </p>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleReassign}
            disabled={reassignEvidence.isPending}
          >
            {reassignEvidence.isPending ? "Reassigning..." : "Reassign"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export function DeleteEvidenceDialog({
  evidence,
  trigger,
  open: controlledOpen,
  onOpenChange: setControlledOpen,
  onSuccess,
}: {
  evidence: Evidence;
  trigger?: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onSuccess?: () => void;
}) {
  const [internalOpen, setInternalOpen] = useState(false);
  const isControlled = controlledOpen !== undefined;
  const open = isControlled ? controlledOpen : internalOpen;
  const setOpen = (val: boolean) => {
    if (isControlled) {
      setControlledOpen?.(val);
    } else {
      setInternalOpen(val);
    }
  };

  const deleteEvidence = useDeleteEvidence();
  const router = useRouter();

  const handleDelete = async () => {
    try {
      await deleteEvidence.mutateAsync(evidence.id);
      toast.add({
        title: "Evidence Deleted",
        description: `"${evidence.filename}" has been permanently deleted.`,
        type: "success",
      });
      setOpen(false);
      if (onSuccess) {
        onSuccess();
      } else {
        router.push("/evidence");
      }
    } catch (error) {
      // Extract a meaningful message from the error
      let description = "Could not delete evidence.";
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const data = error.response?.data as Record<string, unknown> | undefined;
        const detail = (data?.detail as string) || (data?.message as string);
        if (status === 401) {
          description = "Your session has expired. Please log in again.";
        } else if (status === 403) {
          description = "You do not have permission to delete this evidence.";
        } else if (status === 404) {
          description = "Evidence no longer exists.";
        } else if (status === 409) {
          description = detail || "Evidence cannot be deleted because it is protected.";
        } else if (status && status >= 500) {
          description = detail || "Evidence could not be deleted. Please try again.";
        } else if (!error.response) {
          description = "Could not reach the CrimeKit server.";
        } else if (detail) {
          description = detail;
        }
      } else if (error instanceof Error) {
        description = error.message || description;
      }
      toast.add({
        title: "Delete Failed",
        description,
        type: "error",
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {trigger && <DialogTrigger render={trigger as React.ReactElement} />}
      {!trigger && !isControlled && (
        <DialogTrigger render={<Button variant="destructive" size="sm" className="gap-1" />}>
          <Trash2 className="h-3.5 w-3.5" />
          Delete
        </DialogTrigger>
      )}
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Delete Evidence</DialogTitle>
          <DialogDescription>
            Are you sure you want to permanently delete &quot;{evidence.filename}&quot;?
            This permanently deletes the evidence. Chain of custody and audit history will be preserved.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deleteEvidence.isPending}
          >
            {deleteEvidence.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              "Delete Permanently"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
