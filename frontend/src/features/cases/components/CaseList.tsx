"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useCases } from "@/hooks/queries/useCases";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  MoreHorizontal,
  ExternalLink,
  FileText,
  Pencil,
  Trash2,
} from "lucide-react";
import { CreateCaseDialog } from "@/features/cases/components/CreateCaseDialog";
import { EditCaseDialog } from "@/features/cases/components/EditCaseDialog";
import { DeleteCaseDialog } from "@/features/cases/components/DeleteCaseDialog";
import { StatusUpdateDropdown } from "@/features/cases/components/StatusUpdateDropdown";
import type { CaseOut } from "@/types/case";

export function CaseList() {
  const router = useRouter();
  const { data, isLoading, isError } = useCases();
  const cases = data?.items ?? [];
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleCaseCreated = useCallback(
    (createdCase: CaseOut) => {
      setDialogOpen(false);
      router.push(`/workspace/${createdCase.id}`);
    },
    [router],
  );

  if (isError) {
    return <div className="text-destructive">Failed to load cases.</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">All Cases</h2>
        <CreateCaseDialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          onCreated={handleCaseCreated}
        />
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Case ID</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Creator</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[200px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[80px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[120px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[60px]" /></TableCell>
                </TableRow>
              ))
            ) : cases.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center h-24">
                  No cases found.
                </TableCell>
              </TableRow>
            ) : (
              cases.map((caseItem) => (
                <CaseRow key={caseItem.id} caseItem={caseItem} />
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

function CaseRow({ caseItem }: { caseItem: CaseOut }) {
  const router = useRouter();
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);

  return (
    <TableRow>
      <TableCell className="font-mono text-xs">
        {caseItem.id.split("-")[0]}
      </TableCell>

      <TableCell className="font-medium">
        {caseItem.title}
      </TableCell>

      <TableCell>
        <StatusUpdateDropdown caseItem={caseItem} />
      </TableCell>

      <TableCell className="text-muted-foreground text-sm">
        {caseItem.created_by || "System"}
      </TableCell>

      <TableCell className="text-right">
        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <button className="inline-flex items-center justify-center h-8 w-8 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors">
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">Actions</span>
              </button>
            }
          />
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem
              onClick={() => router.push(`/workspace/${caseItem.id}`)}
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Open Workspace
            </DropdownMenuItem>

            <DropdownMenuItem
              onClick={() => router.push(`/cases/${caseItem.id}`)}
            >
              <FileText className="h-4 w-4 mr-2" />
              View Details
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem onClick={() => setEditOpen(true)}>
              <Pencil className="h-4 w-4 mr-2" />
              Edit Case
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem
              onClick={() => setDeleteOpen(true)}
              className="text-destructive focus:text-destructive"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Case
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <EditCaseDialog
          caseItem={caseItem}
          open={editOpen}
          onOpenChange={setEditOpen}
        />
        <DeleteCaseDialog
          caseItem={caseItem}
          open={deleteOpen}
          onOpenChange={setDeleteOpen}
        />
      </TableCell>
    </TableRow>
  );
}
