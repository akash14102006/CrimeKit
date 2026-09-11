"use client";

import { useRouter } from "next/navigation";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { useCases } from "@/hooks/queries/useCases";
import { Brain, Loader2, FolderOpen } from "lucide-react";
import { Button } from "@/components/ui/button";

function AISelectCase() {
  const router = useRouter();
  const { data, isLoading } = useCases({ page: 1, limit: 50 });
  const cases = data?.items ?? [];

  if (isLoading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
      <div className="max-w-lg w-full space-y-6 text-center">
        <Brain className="h-12 w-12 mx-auto text-primary/40" />
        <h2 className="text-xl font-semibold">AI Investigation Workspace</h2>
        <p className="text-sm text-muted-foreground">
          Select a case to open the AI workspace for that investigation.
        </p>

        {cases.length === 0 ? (
          <div className="rounded-lg border border-dashed p-8 space-y-3">
            <FolderOpen className="h-8 w-8 mx-auto text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">
              No cases found. Create a case first.
            </p>
            <Button variant="outline" size="sm" onClick={() => router.push("/cases")}>
              Go to Cases
            </Button>
          </div>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {cases.map((c) => (
              <button
                key={c.id}
                onClick={() => router.push(`/ai/${c.id}`)}
                className="w-full flex items-center gap-3 rounded-lg border p-3 text-left hover:bg-muted/50 transition-colors"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded bg-primary/10 text-xs font-bold text-primary shrink-0">
                  {c.title?.[0]?.toUpperCase() ?? "C"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{c.title}</p>
                  {c.description && (
                    <p className="text-xs text-muted-foreground truncate">
                      {c.description}
                    </p>
                  )}
                </div>
                <span className="text-xs text-muted-foreground shrink-0">
                  {c.status}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function AISelectCasePage() {
  return (
    <AuthGuard allowedRoles={["admin", "investigator", "analyst"]}>
      <AISelectCase />
    </AuthGuard>
  );
}
