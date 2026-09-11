"use client";

import { useCallback, useState } from "react";
import Link from "next/link";
import {
  Search,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  FileText,
  Image as ImageIcon,
  Video,
  HardDrive,
  MoreHorizontal,
  Eye,
  Download,
  Trash2,
  Download as ExportIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectItem,
  SelectPopup,
  SelectPositioner,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Skeleton } from "@/components/ui/skeleton";
import { useAllEvidence } from "@/hooks/queries/useEvidence";
import { useDebounce } from "@/hooks/useDebounce";
import { ErrorState } from "@/components/shared/ErrorState";
import { EmptyState } from "@/components/shared/EmptyState";
import { useRBAC } from "@/hooks/useRBAC";
import { DeleteEvidenceDialog } from "./EvidenceActions";
import { BulkActions } from "./BulkActions";
import { evidenceService } from "@/services/evidenceService";
import { exportEvidenceToCSV } from "../lib/export";
import { formatBytes } from "@/lib/utils";
import type { Evidence } from "@/types/evidence";
import { OpenDiskAnalyzerAction } from "./OpenDiskAnalyzerAction";

type SortField = "filename" | "size" | "uploaded_at" | "mime_type";
type SortDir = "asc" | "desc";

function getFileIcon(mimeType: string | null) {
  if (!mimeType) return <FileText className="h-4 w-4 text-muted-foreground" />;
  if (mimeType.startsWith("image/")) return <ImageIcon className="h-4 w-4 text-green-500" />;
  if (mimeType.startsWith("video/")) return <Video className="h-4 w-4 text-purple-500" />;
  if (mimeType.includes("pdf")) return <FileText className="h-4 w-4 text-red-500" />;
  return <HardDrive className="h-4 w-4 text-orange-500" />;
}

function SortIndicator({ field, currentField, currentDir }: { field: SortField; currentField: SortField; currentDir: SortDir }) {
  if (currentField !== field)
    return <ArrowUpDown className="h-3.5 w-3.5 ml-1 opacity-40" />;
  return currentDir === "asc" ? (
    <ArrowUp className="h-3.5 w-3.5 ml-1" />
  ) : (
    <ArrowDown className="h-3.5 w-3.5 ml-1" />
  );
}

function EvidenceRowActions({ item, onRefresh }: { item: Evidence; onRefresh: () => void }) {
  const { hasPermission } = useRBAC();
  const canDelete = hasPermission("evidence:delete");
  const [deleteOpen, setDeleteOpen] = useState(false);

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger className="inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground h-8 w-8 focus:outline-none">
          <MoreHorizontal className="h-4 w-4" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem render={<Link href={`/evidence/${item.id}`} className="flex items-center gap-2" />}>
            <Eye className="h-4 w-4" /> View Details
          </DropdownMenuItem>
          <OpenDiskAnalyzerAction evidence={item} variant="menu" />
          <DropdownMenuItem
            className="gap-2"
            onClick={() => evidenceService.download(item.id, item.filename)}
          >
            <Download className="h-4 w-4" /> Download
          </DropdownMenuItem>
          <DropdownMenuItem
            className="gap-2"
            onClick={() => {
              navigator.clipboard.writeText(item.sha256 ?? "");
            }}
          >
            <Download className="h-4 w-4" /> Copy Hash
          </DropdownMenuItem>
          {canDelete && (
            <DropdownMenuItem
              className="gap-2 text-destructive focus:text-destructive cursor-pointer"
              onClick={() => setDeleteOpen(true)}
            >
              <Trash2 className="h-4 w-4" /> Delete
            </DropdownMenuItem>
          )}
        </DropdownMenuContent>
      </DropdownMenu>

      {canDelete && (
        <DeleteEvidenceDialog
          evidence={item}
          open={deleteOpen}
          onOpenChange={setDeleteOpen}
          onSuccess={onRefresh}
        />
      )}
    </>
  );
}

export function EvidenceList() {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [sortField, setSortField] = useState<SortField>("uploaded_at");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [page, setPage] = useState(1);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const debouncedSearch = useDebounce(search, 300);

  const { data, isLoading, isError, refetch } = useAllEvidence({
    page,
    limit: 10,
    search: debouncedSearch || undefined,
    mime_type: typeFilter !== "all" ? typeFilter : undefined,
    sort_by: sortField,
    sort_order: sortDir,
  });

  const evidence = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / 10));

  const toggleSort = useCallback(
    (field: SortField) => {
      if (sortField === field) {
        setSortDir((d) => (d === "asc" ? "desc" : "asc"));
      } else {
        setSortField(field);
        setSortDir("asc");
      }
      setPage(1);
    },
    [sortField],
  );

  const toggleSelectAll = useCallback(() => {
    if (selectedIds.size === evidence.length && evidence.length > 0) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(evidence.map((e) => e.id)));
    }
  }, [evidence, selectedIds.size]);

  const toggleSelect = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const selectedItems = evidence.filter((e) => selectedIds.has(e.id));
  const allSelected = evidence.length > 0 && selectedIds.size === evidence.length;

  if (isError) {
    return (
      <ErrorState
        title="Failed to load evidence"
        description="An error occurred while fetching evidence. Please try again."
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-1 items-center gap-2">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by name, ID, or hash..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="pl-9"
              aria-label="Search evidence"
            />
          </div>
          <Select
            value={typeFilter}
            onValueChange={(val) => {
              if (val) {
                setTypeFilter(val);
                setPage(1);
              }
            }}
          >
            <SelectTrigger className="w-[140px]" aria-label="Filter by type">
              <SelectValue placeholder="All Types" />
            </SelectTrigger>
            <SelectPositioner>
              <SelectPopup>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="image">Images</SelectItem>
                <SelectItem value="video">Video</SelectItem>
                <SelectItem value="document">Documents</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectPopup>
            </SelectPositioner>
          </Select>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSearch("");
              setTypeFilter("all");
              setSortField("uploaded_at");
              setSortDir("desc");
              setPage(1);
            }}
            className="gap-1"
            aria-label="Reset filters"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </Button>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="gap-1"
          onClick={() => exportEvidenceToCSV(evidence, `evidence-page-${page}.csv`)}
        >
          <ExportIcon className="h-3.5 w-3.5" />
          Export CSV
        </Button>
      </div>

      <BulkActions
        selectedItems={selectedItems}
        onClearSelection={() => setSelectedIds(new Set())}
        onRefresh={() => refetch()}
      />

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[40px]">
                <Checkbox
                  checked={allSelected}
                  onCheckedChange={toggleSelectAll}
                  aria-label="Select all"
                />
              </TableHead>
              <TableHead>
                <button onClick={() => toggleSort("filename")} className="inline-flex items-center hover:text-foreground transition-colors">
                  Filename <SortIndicator field="filename" currentField={sortField} currentDir={sortDir} />
                </button>
              </TableHead>
              <TableHead>Type</TableHead>
              <TableHead className="w-[100px]">
                <button onClick={() => toggleSort("size")} className="inline-flex items-center hover:text-foreground transition-colors">
                  Size <SortIndicator field="size" currentField={sortField} currentDir={sortDir} />
                </button>
              </TableHead>
              <TableHead className="w-[120px]">Case</TableHead>
              <TableHead className="w-[140px]">
                <button onClick={() => toggleSort("uploaded_at")} className="inline-flex items-center hover:text-foreground transition-colors">
                  Uploaded <SortIndicator field="uploaded_at" currentField={sortField} currentDir={sortDir} />
                </button>
              </TableHead>
              <TableHead className="text-right w-[80px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-[40px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[200px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[80px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[60px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[40px]" /></TableCell>
                </TableRow>
              ))
            ) : evidence.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7}>
                  <EmptyState
                    title="No evidence found"
                    description={
                      search || typeFilter !== "all"
                        ? "Try adjusting your search or filters."
                        : "Upload your first evidence file to get started."
                    }
                  />
                </TableCell>
              </TableRow>
            ) : (
              evidence.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedIds.has(item.id)}
                      onCheckedChange={() => toggleSelect(item.id)}
                      aria-label={`Select ${item.filename}`}
                    />
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getFileIcon(item.mime_type)}
                      <Link
                        href={`/evidence/${item.id}`}
                        className="font-medium hover:underline truncate max-w-[250px]"
                        title={item.filename}
                      >
                        {item.filename}
                      </Link>
                    </div>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {item.mime_type ?? "Unknown"}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatBytes(item.size)}
                  </TableCell>
                  <TableCell className="text-xs font-mono text-muted-foreground">
                    {item.case_id ? item.case_id.split("-")[0] + "..." : "—"}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {item.uploaded_at
                      ? new Date(item.uploaded_at).toLocaleDateString()
                      : "—"}
                  </TableCell>
                  <TableCell className="text-right">
                    <EvidenceRowActions
                      item={item}
                      onRefresh={() => refetch()}
                    />
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {total > 10 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {(page - 1) * 10 + 1}-
            {Math.min(page * 10, total)} of {total} items
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              aria-label="Previous page"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              aria-label="Next page"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
