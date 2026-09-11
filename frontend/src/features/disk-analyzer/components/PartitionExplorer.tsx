"use client";

import { useState } from "react";
import { HardDrive, FolderTree, File, FileText, Image, Film, Archive, ChevronRight, ChevronDown, Search, Eye, EyeOff } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useDiskAnalyzerStore } from "../store/diskAnalyzerStore";
import { useFilteredFiles } from "../hooks/useDiskAnalyzer";
import { cn, formatBytes } from "@/lib/utils";
import type { TSKFileInfo } from "@/types/tsk";

function getFileIconClass(name: string, objectType: string): string {
  if (objectType === "directory") return "FolderTree";
  const ext = name.split(".").pop()?.toLowerCase() ?? "";
  if (["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"].includes(ext)) return "Image";
  if (["mp4", "avi", "mkv", "mov", "wmv"].includes(ext)) return "Film";
  if (["zip", "rar", "7z", "tar", "gz"].includes(ext)) return "Archive";
  if (["txt", "log", "csv", "xml", "json", "html"].includes(ext)) return "FileText";
  return "File";
}

const ICON_MAP: Record<string, typeof File> = {
  FolderTree,
  File,
  FileText,
  Image,
  Film,
  Archive,
};

interface TreeItemProps {
  file: TSKFileInfo;
  depth: number;
  isSelected: boolean;
  onSelect: (file: TSKFileInfo) => void;
}

function TreeItem({ file, depth, isSelected, onSelect }: TreeItemProps) {
  const [expanded, setExpanded] = useState(depth < 1);
  const iconName = getFileIconClass(file.name, file.object_type);
  const Icon = ICON_MAP[iconName] ?? File;
  const isDir = file.object_type === "directory";

  return (
    <div>
      <button
        onClick={() => {
          if (isDir) setExpanded(!expanded);
          onSelect(file);
        }}
        className={cn(
          "flex w-full items-center gap-1.5 rounded px-2 py-1 text-left text-xs transition-colors hover:bg-accent/50",
          isSelected && "bg-primary/10 text-primary",
          file.is_deleted && "opacity-50 italic",
        )}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
      >
        {isDir ? (
          expanded ? (
            <ChevronDown className="h-3 w-3 shrink-0" />
          ) : (
            <ChevronRight className="h-3 w-3 shrink-0" />
          )
        ) : (
          <span className="w-3" />
        )}
        <Icon className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
        <span className="truncate">{file.name}</span>
        {!isDir && (
          <span className="ml-auto shrink-0 text-muted-foreground">
            {formatBytes(file.size)}
          </span>
        )}
      </button>
      {expanded &&
        isDir &&
        file.children?.map((child) => (
          <TreeItem
            key={child.path}
            file={child}
            depth={depth + 1}
            isSelected={isSelected}
            onSelect={onSelect}
          />
        ))}
    </div>
  );
}

export function PartitionExplorer() {
  const {
    partitions,
    filesystems,
    selectedPartitionIndex,
    selectedFilesystemIndex,
    selectPartition,
    selectFilesystem,
    selectFile,
    selectedFile,
    showDeleted,
    showUnallocated,
    setShowDeleted,
    setShowUnallocated,
    fileFilter,
    setFileFilter,
  } = useDiskAnalyzerStore();

  const filteredFiles = useFilteredFiles();

  return (
    <div className="flex h-full flex-col border-r">
      <div className="border-b px-3 py-2">
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Disk Structure
        </h3>
        <div className="relative mb-2">
          <Search className="absolute left-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Filter files..."
            value={fileFilter}
            onChange={(e) => setFileFilter(e.target.value)}
            className="h-7 pl-7 text-xs"
          />
        </div>
        <div className="flex gap-1">
          <Button
            variant={showDeleted ? "default" : "ghost"}
            size="sm"
            onClick={() => setShowDeleted(!showDeleted)}
            className="h-6 gap-1 text-[10px]"
          >
            {showDeleted ? <Eye className="h-2.5 w-2.5" /> : <EyeOff className="h-2.5 w-2.5" />}
            Deleted
          </Button>
          <Button
            variant={showUnallocated ? "default" : "ghost"}
            size="sm"
            onClick={() => setShowUnallocated(!showUnallocated)}
            className="h-6 gap-1 text-[10px]"
          >
            {showUnallocated ? <Eye className="h-2.5 w-2.5" /> : <EyeOff className="h-2.5 w-2.5" />}
            Unallocated
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        {partitions.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-6 text-center">
            <HardDrive className="mb-2 h-8 w-8 text-muted-foreground/30" />
            <p className="text-xs text-muted-foreground">
              No partitions detected. Run TSK analysis to begin.
            </p>
          </div>
        ) : (
          <div className="p-2">
            <div className="mb-2 space-y-1">
              {partitions.map((p) => {
                return (
                  <div key={p.index}>
                    <button
                      onClick={() =>
                        selectPartition(selectedPartitionIndex === p.index ? null : p.index)
                      }
                      className={cn(
                        "flex w-full items-center gap-2 rounded px-2 py-1.5 text-xs transition-colors hover:bg-accent/50",
                        selectedPartitionIndex === p.index && "bg-primary/10 text-primary",
                      )}
                    >
                      <HardDrive className="h-3 w-3 shrink-0 text-muted-foreground" />
                      <span className="font-medium">Partition {p.index}</span>
                      <span className="ml-auto text-muted-foreground">
                        {formatBytes(p.length)}
                      </span>
                    </button>
                    {selectedPartitionIndex === p.index && (
                      <div className="ml-4 mt-1 space-y-0.5">
                        {filesystems
                          .filter((fs) => fs.source_partition === p.index)
                          .map((fs, i) => (
                            <button
                              key={`${p.index}-${i}`}
                              onClick={() =>
                                selectFilesystem(
                                  selectedFilesystemIndex === filesystems.indexOf(fs)
                                    ? null
                                    : filesystems.indexOf(fs),
                                )
                              }
                              className={cn(
                                "flex w-full items-center gap-2 rounded px-2 py-1 text-xs transition-colors hover:bg-accent/50",
                                selectedFilesystemIndex === filesystems.indexOf(fs) &&
                                  "bg-accent text-accent-foreground",
                              )}
                            >
                              <FolderTree className="h-3 w-3 shrink-0" />
                              <span>{fs.fs_type.toUpperCase()}</span>
                              <span className="text-muted-foreground">
                                {formatBytes(fs.block_size * fs.block_count)}
                              </span>
                            </button>
                          ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {filteredFiles.length > 0 && (
              <>
                <div className="mb-1 border-t pt-2">
                  <span className="px-2 text-[10px] font-semibold uppercase text-muted-foreground">
                    Files ({filteredFiles.length})
                  </span>
                </div>
                {filteredFiles.slice(0, 500).map((file) => (
                  <TreeItem
                    key={file.path}
                    file={file}
                    depth={0}
                    isSelected={selectedFile?.path === file.path}
                    onSelect={selectFile}
                  />
                ))}
                {filteredFiles.length > 500 && (
                  <div className="px-2 py-1 text-[10px] text-muted-foreground">
                    Showing 500 of {filteredFiles.length} files. Use search to narrow results.
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
