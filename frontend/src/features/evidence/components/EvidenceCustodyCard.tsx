"use client";

import { useState } from "react";
import { Clock, User, MapPin, FileText, Plus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { useEvidenceCustody, useAppendCustody } from "@/hooks/queries/useEvidence";
import { toast } from "@/components/ui/toast";
import { useAuthStore } from "@/store/authStore";

interface Props {
  evidenceId: string;
}

export function EvidenceCustodyCard({ evidenceId }: Props) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [action, setAction] = useState("");
  const [location, setLocation] = useState("");
  const [notes, setNotes] = useState("");
  const { user } = useAuthStore();
  const { data: custody, isLoading, isError } = useEvidenceCustody(evidenceId);
  const appendCustody = useAppendCustody();

  const handleSubmit = async () => {
    if (!action.trim()) return;
    try {
      await appendCustody.mutateAsync({
        evidenceId,
        payload: {
          action: action.trim(),
          new_owner: user?.id ?? "unknown",
          location: location.trim() || undefined,
          notes: notes.trim() || undefined,
        },
      });
      toast.add({ title: "Custody Entry Added", description: "Chain of custody updated.", type: "success" });
      setDialogOpen(false);
      setAction("");
      setLocation("");
      setNotes("");
    } catch {
      toast.add({ title: "Failed", description: "Could not add custody entry.", type: "error" });
    }
  };

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Chain of Custody</CardTitle>
          <Button variant="outline" size="sm" onClick={() => setDialogOpen(true)} className="gap-1">
            <Plus className="h-3.5 w-3.5" />
            Add Entry
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex gap-3">
                  <Skeleton className="h-8 w-8 rounded-full shrink-0" />
                  <div className="flex-1 space-y-1">
                    <Skeleton className="h-4 w-[150px]" />
                    <Skeleton className="h-3 w-[200px]" />
                  </div>
                </div>
              ))}
            </div>
          ) : isError ? (
            <p className="text-sm text-muted-foreground">Failed to load custody chain.</p>
          ) : !custody?.history?.length ? (
            <p className="text-sm text-muted-foreground">No custody entries recorded.</p>
          ) : (
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />
              <div className="space-y-4">
                {custody.history.map((entry) => {
                  const details = (entry.details ?? {}) as Record<string, string>;
                  return (
                    <div key={entry.id} className="flex gap-3 relative">
                      <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center shrink-0 z-10">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium capitalize">{entry.action}</p>
                        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground mt-0.5">
                          {entry.actor_id && (
                            <span className="flex items-center gap-1">
                              <User className="h-3 w-3" />
                              {entry.actor_id.split("-")[0]}...
                            </span>
                          )}
                          {entry.timestamp && (
                            <span>{new Date(entry.timestamp).toLocaleString()}</span>
                          )}
                          {details.location && (
                            <span className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              {details.location}
                            </span>
                          )}
                        </div>
                        {details.notes && (
                          <p className="text-xs text-muted-foreground mt-1 flex items-start gap-1">
                            <FileText className="h-3 w-3 shrink-0 mt-0.5" />
                            {details.notes}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Custody Entry</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Action *</Label>
              <Input
                value={action}
                onChange={(e) => setAction(e.target.value)}
                placeholder="e.g. transferred, inspected, stored"
              />
            </div>
            <div>
              <Label>Location</Label>
              <Input
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Evidence Room A"
              />
            </div>
            <div>
              <Label>Notes</Label>
              <Input
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Optional notes"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSubmit} disabled={!action.trim() || appendCustody.isPending}>
              {appendCustody.isPending ? "Adding..." : "Add Entry"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
