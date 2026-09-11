"use client";

import { useState } from "react";
import {   Building2, Users, ExternalLink } from "lucide-react";
import { useAdminOrganizations, useOrganizationDetail, useOrganizationMembers } from "../hooks/useAdmin";

export function OrganizationPanel() {
  const { data: orgs, isLoading } = useAdminOrganizations();
  const [selectedOrg, setSelectedOrg] = useState<string | null>(null);
  const { data: orgDetail } = useOrganizationDetail(selectedOrg);
  const { data: members } = useOrganizationMembers(selectedOrg);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-24 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Building2 className="h-5 w-5" />
        <h2 className="text-lg font-semibold">Organization Management</h2>
        <span className="text-sm text-muted-foreground">
          ({orgs?.length ?? 0} organizations)
        </span>
      </div>

      <div className="grid gap-3">
        {orgs?.map((org) => (
          <button
            key={org.id}
            onClick={() => setSelectedOrg(selectedOrg === org.id ? null : org.id)}
            className="flex items-center gap-4 rounded-lg border bg-card p-4 text-left hover:bg-muted/50"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <Building2 className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium">{org.name}</p>
              {org.description && (
                <p className="text-xs text-muted-foreground truncate">
                  {org.description}
                </p>
              )}
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              {org.plan && (
                <span className="rounded-full bg-muted px-2 py-0.5">{org.plan}</span>
              )}
              <span
                className={`h-2 w-2 rounded-full ${
                  org.is_active ? "bg-green-500" : "bg-red-500"
                }`}
              />
              <ExternalLink className="h-3 w-3" />
            </div>
          </button>
        ))}

        {(!orgs || orgs.length === 0) && (
          <div className="flex h-24 items-center justify-center rounded-lg border border-dashed">
            <p className="text-sm text-muted-foreground">No organizations found</p>
          </div>
        )}
      </div>

      {selectedOrg && orgDetail && (
        <div className="rounded-lg border bg-card p-4 space-y-3">
          <h3 className="font-medium">{orgDetail.name} — Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
            <div>
              <span className="text-muted-foreground">Projects:</span>
              <span className="ml-2 font-medium">{orgDetail.projects}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Members:</span>
              <span className="ml-2 font-medium">{orgDetail.members}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Cases:</span>
              <span className="ml-2 font-medium">{orgDetail.cases}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Evidence:</span>
              <span className="ml-2 font-medium">{orgDetail.evidence}</span>
            </div>
          </div>
        </div>
      )}

      {selectedOrg && members && (
        <div className="rounded-lg border bg-card p-4 space-y-3">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            <h3 className="font-medium">Members</h3>
            <span className="text-xs text-muted-foreground">
              ({members.length})
            </span>
          </div>
          <div className="space-y-2">
            {members.map((m) => (
              <div
                key={m.user_id}
                className="flex items-center justify-between rounded border p-2 text-sm"
              >
                <span className="font-mono text-xs">{m.user_id}</span>
                <span className="rounded-full bg-muted px-2 py-0.5 text-xs">
                  {m.role}
                </span>
              </div>
            ))}
            {members.length === 0 && (
              <p className="text-xs text-muted-foreground">No members</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
