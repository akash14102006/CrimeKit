"use client";

import { useMemo } from "react";
import { Users, Mail, Globe, FileText, Tag, Hash } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useDiskAnalyzerStore } from "../store/diskAnalyzerStore";
import type { TSKArtifact } from "@/types/tsk";

interface Entity {
  type: string;
  value: string;
  count: number;
  artifacts: TSKArtifact[];
}

const ENTITY_ICONS: Record<string, typeof FileText> = {
  email: Mail,
  url: Globe,
  ip: Globe,
  filename: FileText,
  person: Users,
  hash: Hash,
  phone: Users,
};

function extractEntitiesFromArtifacts(artifacts: TSKArtifact[]): Entity[] {
  const entityMap = new Map<string, Entity>();

  for (const artifact of artifacts) {
    const fileName = artifact.file_name.toLowerCase();

    if (fileName.includes("@")) {
      const key = `email:${artifact.file_name}`;
      const existing = entityMap.get(key);
      if (existing) {
        existing.count++;
      } else {
        entityMap.set(key, {
          type: "email",
          value: artifact.file_name,
          count: 1,
          artifacts: [artifact],
        });
      }
    }

    if (artifact.file_path.includes("/")) {
      const parts = artifact.file_path.split("/");
      const dir = parts.slice(0, -1).join("/");
      if (dir) {
        const key = `path:${dir}`;
        const existing = entityMap.get(key);
        if (existing) {
          existing.count++;
        } else {
          entityMap.set(key, {
            type: "path",
            value: dir,
            count: 1,
            artifacts: [artifact],
          });
        }
      }
    }

    if (artifact.content_hash) {
      const key = `hash:${artifact.content_hash.slice(0, 16)}`;
      const existing = entityMap.get(key);
      if (existing) {
        existing.count++;
      } else {
        entityMap.set(key, {
          type: "hash",
          value: artifact.content_hash,
          count: 1,
          artifacts: [artifact],
        });
      }
    }

    const ext = artifact.file_name.split(".").pop()?.toLowerCase();
    if (ext) {
      const key = `ext:${ext}`;
      const existing = entityMap.get(key);
      if (existing) {
        existing.count++;
        existing.artifacts.push(artifact);
      } else {
        entityMap.set(key, {
          type: "filetype",
          value: ext,
          count: 1,
          artifacts: [artifact],
        });
      }
    }
  }

  return Array.from(entityMap.values()).sort((a, b) => b.count - a.count);
}

export function EntitiesPanel() {
  const { artifacts } = useDiskAnalyzerStore();
  const entities = useMemo(() => extractEntitiesFromArtifacts(artifacts), [artifacts]);

  if (entities.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-6 text-center">
        <Users className="mb-2 h-8 w-8 text-muted-foreground/30" />
        <p className="text-xs text-muted-foreground">
          No entities extracted yet. Run TSK analysis to discover entities.
        </p>
      </div>
    );
  }

  const grouped = entities.reduce(
    (acc, e) => {
      if (!acc[e.type]) acc[e.type] = [];
      acc[e.type].push(e);
      return acc;
    },
    {} as Record<string, Entity[]>,
  );

  return (
    <div className="flex h-full flex-col">
      <div className="border-b px-4 py-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Extracted Entities ({entities.length})
        </h3>
      </div>
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {Object.entries(grouped).map(([type, items]) => {
            const Icon = ENTITY_ICONS[type] ?? Tag;
            return (
              <Card key={type}>
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center gap-2 text-xs">
                    <Icon className="h-3.5 w-3.5" />
                    {type.charAt(0).toUpperCase() + type.slice(1)}s
                    <Badge variant="secondary" className="ml-auto text-[10px]">
                      {items.length}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-1">
                  {items.slice(0, 20).map((entity, i) => (
                    <div
                      key={`${entity.value}-${i}`}
                      className="flex items-center justify-between rounded px-2 py-1 text-xs hover:bg-accent/50"
                    >
                      <span className="truncate font-mono text-[11px]">{entity.value}</span>
                      <Badge variant="outline" className="ml-2 shrink-0 text-[10px]">
                        {entity.count}
                      </Badge>
                    </div>
                  ))}
                  {items.length > 20 && (
                    <p className="py-1 text-center text-[10px] text-muted-foreground">
                      + {items.length - 20} more
                    </p>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
}
