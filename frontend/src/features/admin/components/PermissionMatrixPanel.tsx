"use client";

import { useMemo } from "react";
import { Grid3x3 } from "lucide-react";
import { ROLES, ROLE_LABELS, ROLE_PERMISSIONS, PERMISSIONS } from "@/constants/roles";

export function PermissionMatrixPanel() {
  const matrix = useMemo(() => {
    return PERMISSIONS.map((perm) => ({
      permission: perm,
      roles: ROLES.map((role) => ({
        role,
        granted: ROLE_PERMISSIONS[role]?.includes(perm) ?? false,
      })),
    }));
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Grid3x3 className="h-5 w-5" />
        <h2 className="text-lg font-semibold">Permission Matrix</h2>
      </div>

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="p-2 text-left font-medium">Permission</th>
              {ROLES.map((role) => (
                <th
                  key={role}
                  className="p-2 text-center font-medium"
                  title={role}
                >
                  <span className="text-xs">
                    {ROLE_LABELS[role]?.split(" ")[0] ?? role}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.map(({ permission, roles }) => (
              <tr key={permission} className="border-b last:border-0">
                <td className="p-2 font-mono text-xs">{permission}</td>
                {roles.map(({ role, granted }) => (
                  <td key={role} className="p-2 text-center">
                    <span
                      className={`inline-block h-4 w-4 rounded ${
                        granted ? "bg-green-500" : "bg-muted"
                      }`}
                      title={granted ? `${ROLE_LABELS[role]}: granted` : `${ROLE_LABELS[role]}: denied`}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <span className="inline-block h-3 w-3 rounded bg-green-500" />
          Granted
        </div>
        <div className="flex items-center gap-1">
          <span className="inline-block h-3 w-3 rounded bg-muted" />
          Denied
        </div>
      </div>
    </div>
  );
}
