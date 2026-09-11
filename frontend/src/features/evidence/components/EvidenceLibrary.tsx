"use client";

import { useState } from "react";
import Link from "next/link";
import { Search, Filter, MoreHorizontal, FileText, Image as ImageIcon, Video, HardDrive, Download, Eye, UploadCloud } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { UploadManager } from "./UploadManager";
import { useAllEvidence, useCaseEvidence } from "@/hooks/queries/useEvidence";
import { useRBAC } from "@/hooks/useRBAC";
import { DeleteEvidenceDialog } from "./EvidenceActions";
import { evidenceService } from "@/services/evidenceService";
import { useCases } from "@/hooks/queries/useCases";
import type { Evidence } from "@/types/evidence";
import { OpenDiskAnalyzerAction } from "./OpenDiskAnalyzerAction";

const formatBytes = (bytes: number, decimals = 2) => {
  if (!+bytes) return '0 Bytes'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

const getIconForType = (type: string) => {
  switch (type) {
    case "document": return <FileText className="h-4 w-4 text-blue-500" />;
    case "image": return <ImageIcon className="h-4 w-4 text-green-500" />;
    case "video": return <Video className="h-4 w-4 text-purple-500" />;
    case "mobile": return <HardDrive className="h-4 w-4 text-orange-500" />;
    case "disk": return <HardDrive className="h-4 w-4 text-red-500" />;
    default: return <FileText className="h-4 w-4 text-muted-foreground" />;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case "processed": return <Badge className="bg-success/20 text-success hover:bg-success/30 border-none">Processed</Badge>;
    case "processing": return <Badge variant="secondary" className="animate-pulse">Processing (78%)</Badge>;
    case "queued": return <Badge variant="outline">Queued for AI</Badge>;
    case "error": return <Badge variant="destructive">Failed</Badge>;
    default: return <Badge variant="outline">{status}</Badge>;
  }
};

export function EvidenceLibrary() {
  const { hasPermission } = useRBAC();
  const canDelete = hasPermission("evidence:delete");

  const [searchTerm, setSearchTerm] = useState("");
  const [caseSearch, setCaseSearch] = useState("");
  const [selectedCaseId, setSelectedCaseId] = useState("");
  const [uploadOpen, setUploadOpen] = useState(false);
  const { data: response, isLoading, refetch } = useAllEvidence({ page: 1, limit: 100 });
  const { data: casesData } = useCases({ page: 1, limit: 50 });
  const evidenceData = response?.items;
  const cases = casesData?.items ?? [];

  const filteredCases = cases.filter((c) => {
    if (!caseSearch) return true;
    const q = caseSearch.toLowerCase();
    return (
      c.id.toLowerCase().includes(q) ||
      c.title.toLowerCase().includes(q) ||
      (c.description ?? "").toLowerCase().includes(q)
    );
  });

  const filteredEvidence = (evidenceData || []).filter((e: { filename?: string; id?: string }) => 
    (e.filename || "").toLowerCase().includes(searchTerm.toLowerCase()) || 
    (e.id || "").toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleOpenUpload = () => {
    if (!selectedCaseId) return;
    setUploadOpen(true);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="relative w-[300px]">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search evidence by name or ID..." 
              className="pl-9"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Button variant="outline" size="icon"><Filter className="h-4 w-4" /></Button>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative w-[280px]">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Select case to upload to..."
              className="pl-9"
              value={caseSearch}
              onChange={(e) => {
                setCaseSearch(e.target.value);
                if (!e.target.value) setSelectedCaseId("");
              }}
              onFocus={() => setCaseSearch("")}
            />
            {caseSearch && !selectedCaseId && filteredCases.length > 0 && (
              <div className="absolute left-0 right-0 top-full z-50 mt-1 max-h-60 overflow-auto rounded-lg border bg-background shadow-lg">
                {filteredCases.slice(0, 10).map((c) => (
                  <button
                    key={c.id}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors"
                    onClick={() => {
                      setSelectedCaseId(c.id);
                      setCaseSearch(`${c.title} (${c.id.slice(0, 8)})`);
                    }}
                  >
                    <div className="font-medium truncate">{c.title}</div>
                    <div className="text-xs text-muted-foreground font-mono">{c.id.slice(0, 8)}... &middot; {c.status}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
          <Button
            onClick={handleOpenUpload}
            disabled={!selectedCaseId}
            className="gap-2"
          >
            <UploadCloud className="h-4 w-4" />
            Upload Evidence
          </Button>
          {!selectedCaseId && (
            <p className="text-xs text-muted-foreground">Select a case before uploading evidence.</p>
          )}
          <UploadManager initialCaseId={selectedCaseId || undefined} open={uploadOpen} onOpenChange={setUploadOpen} trigger={null} />
        </div>
      </div>

      <div className="border rounded-lg bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[100px]">ID</TableHead>
              <TableHead>File Name</TableHead>
              <TableHead>Case</TableHead>
              <TableHead>Size</TableHead>
              <TableHead>Uploaded</TableHead>
              <TableHead>AI Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                  Loading evidence...
                </TableCell>
              </TableRow>
            ) : filteredEvidence.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                  No evidence found matching your search.
                </TableCell>
              </TableRow>
            ) : (
              filteredEvidence.map((evidence) => (
                <TableRow key={evidence.id}>
                  <TableCell className="font-medium">
                    <div className="w-[80px] truncate" title={evidence.id}>{evidence.id ? evidence.id.split('-')[0] : 'N/A'}...</div>
                  </TableCell>
                  <TableCell>
                    <Link href={`/evidence/${evidence.id}`} className="flex items-center gap-2 hover:underline">
                      {getIconForType(evidence.mime_type?.includes('image') ? 'image' : evidence.mime_type?.includes('video') ? 'video' : 'document')}
                      <span className="truncate max-w-[200px]" title={evidence.filename}>{evidence.filename || 'Untitled'}</span>
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="truncate max-w-[100px]" title={evidence.case_id || 'Unassigned'}>
                      {evidence.case_id ? (evidence.case_id.split('-')[0] + '...') : 'Unassigned'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{formatBytes(evidence.size || 0)}</TableCell>
                  <TableCell className="text-muted-foreground">{evidence.uploaded_at ? new Date(evidence.uploaded_at).toLocaleDateString() : 'N/A'}</TableCell>
                  <TableCell>{getStatusBadge("processed")}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <DropdownMenu>
                        <DropdownMenuTrigger className="inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-accent hover:text-accent-foreground h-8 w-8 focus:outline-none">
                          <MoreHorizontal className="h-4 w-4" />
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem render={<Link href={`/evidence/${evidence.id}`} className="flex items-center gap-2" />}>
                            <Eye className="h-4 w-4" /> Open in Viewer
                          </DropdownMenuItem>
                          <OpenDiskAnalyzerAction evidence={evidence as Evidence} variant="menu" />
                          <DropdownMenuItem
                            className="gap-2"
                            onClick={() => evidenceService.download(evidence.id, evidence.filename)}
                          >
                            <Download className="h-4 w-4" /> Download Original
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>

                      {canDelete && (
                        <DeleteEvidenceDialog
                          evidence={evidence as Evidence}
                          onSuccess={() => refetch()}
                        />
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
