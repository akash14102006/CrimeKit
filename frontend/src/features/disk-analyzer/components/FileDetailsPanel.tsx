"use client";

import { File, Hash, Clock, Shield, Tag, User, HardDrive } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useDiskAnalyzerStore } from "../store/diskAnalyzerStore";
import { cn, formatBytes } from "@/lib/utils";

function DataRow({ label, value, icon: Icon, mono }: { label: string; value: string | number | null | undefined; icon?: typeof File; mono?: boolean }) {
  if (value == null || value === "") return null;
  return (
    <div className="flex items-start gap-2 py-1">
      {Icon && <Icon className="mt-0.5 h-3 w-3 shrink-0 text-muted-foreground" />}
      <span className="w-24 shrink-0 text-xs text-muted-foreground">{label}</span>
      <span className={cn("break-all text-xs", mono && "font-mono")}>{String(value)}</span>
    </div>
  );
}

export function FileDetailsPanel() {
  const { selectedFile, selectedArtifact, artifacts } = useDiskAnalyzerStore();

  const file = selectedFile;
  const artifact = selectedArtifact ?? (file ? artifacts.find((a) => a.file_path === file.path) : null);

  if (!file && !artifact) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-6 text-center">
        <File className="mb-2 h-8 w-8 text-muted-foreground/30" />
        <p className="text-xs text-muted-foreground">
          Select a file or artifact to view details
        </p>
      </div>
    );
  }

  if (file) {
    return (
      <ScrollArea className="h-full p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <File className="h-5 w-5 text-primary" />
            <div>
              <h3 className="text-sm font-semibold">{file.name}</h3>
              <p className="text-xs text-muted-foreground font-mono">{file.path}</p>
            </div>
          </div>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs">File Properties</CardTitle>
            </CardHeader>
            <CardContent className="space-y-0.5">
              <DataRow label="Size" value={formatBytes(file.size)} icon={HardDrive} />
              <DataRow label="Type" value={file.object_type} icon={Tag} />
              <DataRow label="FS Type" value={file.fs_type?.toUpperCase()} icon={Tag} />
              <DataRow
                label="Allocation"
                value={file.allocation_state}
                icon={Shield}
              />
              <DataRow label="Metadata Addr" value={file.metadata_addr} icon={Hash} mono />
              <DataRow label="UID" value={file.uid} icon={User} />
              <DataRow label="GID" value={file.gid} icon={User} />
              <DataRow label="Mode" value={`0${file.mode?.toString(8)}`} icon={Tag} mono />
              <DataRow label="Links" value={file.nlink} icon={Hash} />
              {file.is_deleted && (
                <Badge variant="destructive" className="mt-1 text-[10px]">
                  Deleted
                </Badge>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs">Timestamps</CardTitle>
            </CardHeader>
            <CardContent className="space-y-0.5">
              <DataRow label="Access" value={file.atime} icon={Clock} />
              <DataRow label="Modified" value={file.mtime} icon={Clock} />
              <DataRow label="Changed" value={file.ctime} icon={Clock} />
              <DataRow label="Created" value={file.crtime} icon={Clock} />
            </CardContent>
          </Card>

          {artifact && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-xs">Artifact Data</CardTitle>
              </CardHeader>
              <CardContent className="space-y-0.5">
                <DataRow label="Artifact ID" value={artifact.artifact_id} mono />
                <DataRow label="Processor" value={artifact.processor} />
                <DataRow label="Confidence" value={`${(artifact.confidence * 100).toFixed(0)}%`} />
                <DataRow label="Provenance" value={artifact.provenance} />
                <DataRow label="Content Hash" value={artifact.content_hash} mono />
                {Object.entries(artifact.timestamps).map(([k, v]) => (
                  <DataRow key={k} label={k} value={v} icon={Clock} />
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </ScrollArea>
    );
  }

  if (artifact) {
    return (
      <ScrollArea className="h-full p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Tag className="h-5 w-5 text-primary" />
            <div>
              <h3 className="text-sm font-semibold">{artifact.file_name}</h3>
              <p className="text-xs text-muted-foreground font-mono">{artifact.file_path}</p>
            </div>
          </div>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs">Artifact Properties</CardTitle>
            </CardHeader>
            <CardContent className="space-y-0.5">
              <DataRow label="Artifact ID" value={artifact.artifact_id} mono />
              <DataRow label="Processor" value={artifact.processor} />
              <DataRow label="Version" value={artifact.processor_version} />
              <DataRow label="Source" value={artifact.source_image} />
              <DataRow label="Partition" value={artifact.partition_index} />
              <DataRow label="FS Type" value={artifact.filesystem_type?.toUpperCase()} />
              <DataRow label="Type" value={artifact.object_type} />
              <DataRow label="Size" value={formatBytes(artifact.size)} />
              <DataRow label="Allocation" value={artifact.allocation_state} />
              <DataRow label="Confidence" value={`${(artifact.confidence * 100).toFixed(0)}%`} />
              <DataRow label="Provenance" value={artifact.provenance} />
              <DataRow label="Content Hash" value={artifact.content_hash} mono />
              <Separator className="my-2" />
              <span className="text-[10px] font-semibold uppercase text-muted-foreground">Timestamps</span>
              {Object.entries(artifact.timestamps).map(([k, v]) => (
                <DataRow key={k} label={k} value={v} icon={Clock} />
              ))}
            </CardContent>
          </Card>
        </div>
      </ScrollArea>
    );
  }

  return null;
}
