"use client";

import { useMemo } from "react";
import {
  Users,
  Building2,
  Key,
  Shield,

  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { useAdminUsers, useAdminApiKeys, useAdminOrganizations, useAuditVerify } from "../hooks/useAdmin";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: "up" | "down" | "neutral";
  subtitle?: string;
}

function StatCard({ label, value, icon, subtitle }: StatCardProps) {
  return (
    <div className="rounded-lg border bg-card p-4 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-muted-foreground">{icon}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
      {subtitle && (
        <p className="text-xs text-muted-foreground">{subtitle}</p>
      )}
    </div>
  );
}

export function AdminSecurityOverview() {
  const { data: users } = useAdminUsers();
  const { data: apiKeys } = useAdminApiKeys();
  const { data: orgs } = useAdminOrganizations();
  const { data: auditVerify } = useAuditVerify();

  const stats = useMemo(() => {
    const totalUsers = users?.length ?? 0;
    const activeUsers = (users?.filter((u) => u.is_active) ?? []).length;
    const roleBreakdown: Record<string, number> = {};
    users?.forEach((u) =>
      u.roles.forEach((r) => {
        roleBreakdown[r] = (roleBreakdown[r] || 0) + 1;
      })
    );
    const admins = roleBreakdown["admin"] ?? 0;
    const investigators = roleBreakdown["investigator"] ?? 0;
    const totalApiKeys = apiKeys?.length ?? 0;
    const activeApiKeys = (apiKeys?.filter((k) => k.is_active) ?? []).length;
    return {
      totalUsers,
      activeUsers,
      totalOrganizations: orgs?.length ?? 0,
      totalApiKeys,
      activeApiKeys,
      admins,
      investigators,
      auditValid: auditVerify?.is_valid ?? true,
    };
  }, [users, apiKeys, orgs, auditVerify]);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Shield className="h-5 w-5" />
        <h2 className="text-lg font-semibold">Security Overview</h2>
      </div>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <StatCard
          label="Total Users"
          value={stats.totalUsers}
          icon={<Users className="h-4 w-4" />}
          subtitle={`${stats.activeUsers} active`}
        />
        <StatCard
          label="Administrators"
          value={stats.admins}
          icon={<Shield className="h-4 w-4" />}
        />
        <StatCard
          label="Investigators"
          value={stats.investigators}
          icon={<Users className="h-4 w-4" />}
        />
        <StatCard
          label="Organizations"
          value={stats.totalOrganizations}
          icon={<Building2 className="h-4 w-4" />}
        />
        <StatCard
          label="API Keys"
          value={stats.totalApiKeys}
          icon={<Key className="h-4 w-4" />}
          subtitle={`${stats.activeApiKeys} active`}
        />
        <StatCard
          label="Audit Chain"
          value={stats.auditValid ? "Valid" : "Broken"}
          icon={
            stats.auditValid ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <AlertCircle className="h-4 w-4 text-destructive" />
            )
          }
        />
      </div>
    </div>
  );
}
