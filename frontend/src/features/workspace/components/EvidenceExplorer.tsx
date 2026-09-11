"use client";

import { useState, useMemo } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Search,
  FolderTree,
  Image,
  Video,
  FileText,
  Music,
  HardDrive,
  Mail,
  Archive,
  Smartphone,
  Globe,
  Wifi,
  Pin,
  FileIcon,
  UploadCloud,
} from "lucide-react";
import { useWorkspaceEvidence } from "@/hooks/queries/useWorkspace";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { UploadManager } from "@/features/evidence/components/UploadManager";
import type { WorkspaceEvidenceItem } from "@/types/workspace";

interface Props {
  caseId: string;
}

const CATEGORY_ICONS: Record<string, typeof FileText> = {
  image: Image,
  video: Video,
  document: FileText,
  audio: Music,
  disk: HardDrive,
  email: Mail,
  archive: Archive,
  mobile: Smartphone,
  browser: Globe,
  network: Wifi,
  other: FileIcon,
};

const CATEGORY_LABELS: Record<string, string> = {
  image: "Images",
  video: "Videos",
  document: "Documents",
  audio: "Audio",
  disk: "Disk Images",
  email: "Emails",
  archive: "Archives",
  mobile: "Mobile",
  browser: "Browser",
  network: "Network",
  other: "Other",
};

function classifyMime(mime?: string | null): string {
  if (!mime) return "other";
  if (mime.startsWith("image/")) return "image";
  if (mime.startsWith("video/")) return "video";
  if (mime.startsWith("audio/")) return "audio";
  if (mime.includes("pdf") || mime.includes("document") || mime.includes("text/")) return "document";
  if (mime.includes("zip") || mime.includes("tar") || mime.includes("rar") || mime.includes("archive")) return "archive";
  if (mime.includes("email") || mime.includes("message")) return "email";
  if (mime.includes("disk") || mime.includes("iso") || mime.includes("raw")) return "disk";
  if (mime.includes("mobile") || mime.includes("android")) return "mobile";
  if (mime.includes("browser") || mime.includes("sqlite")) return "browser";
  if (mime.includes("pcap") || mime.includes("network")) return "network";
  return "other";
}

function EvidenceTreeItem({
  item,
  isSelected,
  isPinned,
  onSelect,
}: {
  item: WorkspaceEvidenceItem;
  isSelected: boolean;
  isPinned: boolean;
  onSelect: (item: WorkspaceEvidenceItem) => void;
}) {
  const mime = item.mime_type ?? "";
  const category = classifyMime(mime);
  const Icon = CATEGORY_ICONS[category] ?? FileIcon;

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  return (
    <div
      onClick={() => onSelect(item)}
      className={`flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer text-xs transition-colors ${
        isSelected
          ? "bg-primary/10 text-primary border border-primary/20"
          : "hover:bg-muted/50 text-muted-foreground hover:text-foreground"
      }`}
    >
      <Icon className="h-3.5 w-3.5 shrink-0" />
      <span className="truncate flex-1 font-medium" title={item.filename}>
        {item.filename}
      </span>
      {isPinned && <Pin className="h-3 w-3 text-amber-500 shrink-0" />}
      <span className="text-[10px] text-muted-foreground shrink-0">
        {formatSize(item.size)}
      </span>
    </div>
  );
}

export function EvidenceExplorer({ caseId }: Props) {
  const { data: evidence, isLoading } = useWorkspaceEvidence(caseId);
  const [uploadOpen, setUploadOpen] = useState(false);
  const {
    selectedEvidenceId,
    selectEvidence,
    evidenceSearch,
    setEvidenceSearch,
    evidenceFilter,
    setEvidenceFilter,
    pinnedEvidenceIds,
    addRecentEvidence,
  } = useWorkspaceStore();

  const filteredEvidence = useMemo(() => {
    if (!evidence) return [];
    let items = evidence;
    if (evidenceSearch) {
      const q = evidenceSearch.toLowerCase();
      items = items.filter(
        (item) =>
          item.filename.toLowerCase().includes(q) ||
          item.mime_type?.toLowerCase().includes(q) ||
          item.sha256?.toLowerCase().includes(q),
      );
    }
    if (evidenceFilter && evidenceFilter !== "all") {
      items = items.filter((item) => classifyMime(item.mime_type) === evidenceFilter);
    }
    return items;
  }, [evidence, evidenceSearch, evidenceFilter]);

  const categories = useMemo(() => {
    if (!evidence) return [];
    const counts: Record<string, number> = {};
    for (const item of evidence) {
      const cat = classifyMime(item.mime_type);
      counts[cat] = (counts[cat] || 0) + 1;
    }
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([key, count]) => ({ key, count, label: CATEGORY_LABELS[key] ?? key }));
  }, [evidence]);

  const pinnedItems = useMemo(
    () => filteredEvidence.filter((item) => pinnedEvidenceIds.includes(item.id)),
    [filteredEvidence, pinnedEvidenceIds],
  );

  const unpinnedItems = useMemo(
    () => filteredEvidence.filter((item) => !pinnedEvidenceIds.includes(item.id)),
    [filteredEvidence, pinnedEvidenceIds],
  );

  const handleSelect = (item: WorkspaceEvidenceItem) => {
    selectEvidence(item);
    addRecentEvidence(item.id);
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center px-3 py-2 border-b">
        <FolderTree className="h-4 w-4 mr-2 text-muted-foreground" />
        <span className="font-medium text-sm">Evidence Explorer</span>
        <Badge variant="outline" className="ml-auto text-[10px]">
          {evidence?.length ?? 0}
        </Badge>
        <UploadManager initialCaseId={caseId} open={uploadOpen} onOpenChange={setUploadOpen} trigger={null} />
        <Button
          size="sm"
          variant="ghost"
          className="ml-2 h-7 gap-1 text-xs"
          onClick={() => setUploadOpen(true)}
        >
          <UploadCloud className="h-3 w-3" />
          Upload
        </Button>
      </div>

      <div className="px-3 py-2 border-b space-y-2">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            value={evidenceSearch}
            onChange={(e) => setEvidenceSearch(e.target.value)}
            placeholder="Search evidence..."
            className="h-8 pl-7 text-xs"
          />
        </div>
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => setEvidenceFilter("all")}
            className={`px-2 py-0.5 rounded text-[10px] font-medium transition-colors ${
              evidenceFilter === "all"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            All ({evidence?.length ?? 0})
          </button>
          {categories.map((cat) => {
            const Icon = CATEGORY_ICONS[cat.key] ?? FileIcon;
            return (
              <button
                key={cat.key}
                onClick={() => setEvidenceFilter(cat.key)}
                className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium transition-colors ${
                  evidenceFilter === cat.key
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
              >
                <Icon className="h-3 w-3" />
                {cat.label} ({cat.count})
              </button>
            );
          })}
        </div>
      </div>

      <ScrollArea className="flex-1 px-2 py-1">
        {isLoading ? (
          <div className="space-y-2 p-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-8 w-full" />
            ))}
          </div>
        ) : filteredEvidence.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <FolderTree className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-xs text-muted-foreground">
              {evidenceSearch
                ? "No matching evidence"
                : "No evidence added to this case yet."}
            </p>
            {!evidenceSearch && (
              <Button
                size="sm"
                variant="outline"
                className="mt-3 gap-1 text-xs"
                onClick={() => setUploadOpen(true)}
              >
                <UploadCloud className="h-3 w-3" />
                Upload Evidence
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-0.5 py-1">
            {pinnedItems.length > 0 && (
              <>
                <div className="flex items-center gap-1 px-2 py-1 text-[10px] font-medium text-muted-foreground uppercase">
                  <Pin className="h-3 w-3" />
                  Pinned
                </div>
                {pinnedItems.map((item) => (
                  <EvidenceTreeItem
                    key={item.id}
                    item={item}
                    isSelected={selectedEvidenceId === item.id}
                    isPinned
                    onSelect={handleSelect}
                  />
                ))}
                <div className="h-px bg-border mx-2 my-1" />
              </>
            )}
            <div className="flex items-center gap-1 px-2 py-1 text-[10px] font-medium text-muted-foreground uppercase">
              <FileText className="h-3 w-3" />
              All Evidence
            </div>
            {unpinnedItems.map((item) => (
              <EvidenceTreeItem
                key={item.id}
                item={item}
                isSelected={selectedEvidenceId === item.id}
                isPinned={false}
                onSelect={handleSelect}
              />
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
