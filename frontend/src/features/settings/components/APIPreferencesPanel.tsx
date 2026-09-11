"use client";

import { useState } from "react";
import {
  Key,
  Plus,
  RotateCw,
  Trash2,
  Clock,
  AlertCircle,
} from "lucide-react";
import {
  useApiKeys,
  useCreateApiKey,
  useRevokeApiKey,
  useRotateApiKey,
} from "../hooks/useSettings";

export function APIPreferencesPanel() {
  const { data: keys, isLoading } = useApiKeys();
  const createKey = useCreateApiKey();
  const revokeKey = useRevokeApiKey();
  const rotateKey = useRotateApiKey();
  const [showCreate, setShowCreate] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");

  const handleCreate = () => {
    if (!newKeyName.trim()) return;
    createKey.mutate(
      { name: newKeyName.trim() },
      { onSuccess: () => { setNewKeyName(""); setShowCreate(false); } }
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-20 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">API Keys</h2>
          <p className="text-sm text-muted-foreground">
            Manage your personal API keys for programmatic access.
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="inline-flex items-center gap-1 rounded-lg bg-primary px-3 py-1.5 text-sm text-primary-foreground hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Generate Key
        </button>
      </div>

      {showCreate && (
        <div className="flex items-center gap-2 rounded-lg border bg-card p-3">
          <input
            type="text"
            placeholder="Key name (e.g. CI/CD Pipeline)"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            className="flex-1 rounded border bg-background px-3 py-1.5 text-sm"
            onKeyDown={(e) => e.key === "Enter" && handleCreate()}
          />
          <button
            onClick={handleCreate}
            disabled={!newKeyName.trim() || createKey.isPending}
            className="rounded bg-primary px-3 py-1.5 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {createKey.isPending ? "Creating..." : "Create"}
          </button>
          <button
            onClick={() => setShowCreate(false)}
            className="rounded px-3 py-1.5 text-sm text-muted-foreground hover:bg-muted"
          >
            Cancel
          </button>
        </div>
      )}

      <div className="space-y-2">
        {keys?.map((key) => (
          <div
            key={key.id}
            className="flex items-center gap-3 rounded-lg border bg-card p-3"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded bg-primary/10">
              <Key className="h-4 w-4 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium">{key.name}</p>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs ${
                    key.is_active
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {key.is_active ? "Active" : "Revoked"}
                </span>
                <span className="rounded-full bg-muted px-2 py-0.5 text-xs">
                  {key.environment}
                </span>
              </div>
              <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
                <span className="font-mono">{key.key_prefix}</span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {new Date(key.created_at).toLocaleDateString()}
                </span>
                {key.expires_at && (
                  <span className="flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    Expires {new Date(key.expires_at).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1">
              {key.is_active && (
                <>
                  <button
                    onClick={() => rotateKey.mutate(key.id)}
                    className="rounded p-1.5 text-muted-foreground hover:bg-muted"
                    title="Rotate key"
                  >
                    <RotateCw className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => revokeKey.mutate(key.id)}
                    className="rounded p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                    title="Revoke key"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </>
              )}
            </div>
          </div>
        ))}

        {(!keys || keys.length === 0) && (
          <div className="flex h-24 items-center justify-center rounded-lg border border-dashed">
            <p className="text-sm text-muted-foreground">
              No API keys. Create one to get started.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
