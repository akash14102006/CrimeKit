"use client";

import {
  Link2,
  Clock,
  Layers,
  Hash,
  Globe,
  Loader2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useBlockchainStats } from "../hooks/useBlockchain";
import { cn } from "@/lib/utils";

const statCards = [
  {
    key: "total_anchors" as const,
    label: "Total Anchors",
    icon: Link2,
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
  },
  {
    key: "pending_anchors" as const,
    label: "Pending",
    icon: Clock,
    color: "text-amber-500",
    bgColor: "bg-amber-500/10",
  },
  {
    key: "total_batches" as const,
    label: "Batches",
    icon: Layers,
    color: "text-purple-500",
    bgColor: "bg-purple-500/10",
  },
  {
    key: "total_commitments" as const,
    label: "Commitments",
    icon: Hash,
    color: "text-emerald-500",
    bgColor: "bg-emerald-500/10",
  },
];

export function BlockchainStatsPanel() {
  const { data: stats, isLoading, error } = useBlockchainStats();

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Link2 className="h-5 w-5" />
            Blockchain Statistics
          </CardTitle>
          {stats && (
            <Badge variant="secondary" className="gap-1">
              <Globe className="h-3 w-3" />
              {stats.network}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="grid grid-cols-2 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="rounded-lg border p-3 space-y-2">
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-7 w-12" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-8 text-center">
            <p className="text-sm text-muted-foreground">
              Could not load blockchain statistics.
            </p>
          </div>
        ) : stats ? (
          <div className="grid grid-cols-2 gap-3">
            {statCards.map((card) => {
              const Icon = card.icon;
              return (
                <div
                  key={card.key}
                  className="rounded-lg border p-3 transition-colors hover:bg-muted/50"
                >
                  <div className="flex items-center gap-2">
                    <div className={cn("rounded-md p-1.5", card.bgColor)}>
                      <Icon className={cn("h-4 w-4", card.color)} />
                    </div>
                    <span className="text-xs text-muted-foreground">{card.label}</span>
                  </div>
                  <div className="mt-2 text-2xl font-bold font-mono">
                    {stats[card.key].toLocaleString()}
                  </div>
                </div>
              );
            })}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
