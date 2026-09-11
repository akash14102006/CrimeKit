"use client";

import { useAdminStore } from "../store/adminStore";
import type { AdminTab } from "../types/admin";
import { AdminSecurityOverview } from "./AdminSecurityOverview";
import { UserManagementPanel } from "./UserManagementPanel";
import { RoleManagementPanel } from "./RoleManagementPanel";
import { PermissionMatrixPanel } from "./PermissionMatrixPanel";
import { OrganizationPanel } from "./OrganizationPanel";
import { APIKeyPanel } from "./APIKeyPanel";
import { MFAPanel } from "./MFAPanel";
import { AuditPanel } from "./AuditPanel";
import {
  Shield,
  Users,
  ShieldCheck,
  Grid3x3,
  Building2,
  Key,
  Fingerprint,
  ClipboardList,
} from "lucide-react";

const TABS: { key: AdminTab; label: string; icon: React.ReactNode }[] = [
  { key: "overview", label: "Overview", icon: <Shield className="h-4 w-4" /> },
  { key: "users", label: "Users", icon: <Users className="h-4 w-4" /> },
  { key: "roles", label: "Roles", icon: <ShieldCheck className="h-4 w-4" /> },
  { key: "permissions", label: "Permissions", icon: <Grid3x3 className="h-4 w-4" /> },
  { key: "organizations", label: "Organizations", icon: <Building2 className="h-4 w-4" /> },
  { key: "api-keys", label: "API Keys", icon: <Key className="h-4 w-4" /> },
  { key: "mfa", label: "MFA", icon: <Fingerprint className="h-4 w-4" /> },
  { key: "audit", label: "Audit", icon: <ClipboardList className="h-4 w-4" /> },
];

function TabContent({ tab }: { tab: AdminTab }) {
  switch (tab) {
    case "overview":
      return <AdminSecurityOverview />;
    case "users":
      return <UserManagementPanel />;
    case "roles":
      return <RoleManagementPanel />;
    case "permissions":
      return <PermissionMatrixPanel />;
    case "organizations":
      return <OrganizationPanel />;
    case "api-keys":
      return <APIKeyPanel />;
    case "mfa":
      return <MFAPanel />;
    case "audit":
      return <AuditPanel />;
    default:
      return <AdminSecurityOverview />;
  }
}

export function AdminPage() {
  const { activeTab, setActiveTab } = useAdminStore();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Administration</h1>
        <p className="text-muted-foreground">
          Manage users, roles, permissions, organizations, and security settings.
        </p>
      </div>

      <div className="flex gap-1 overflow-x-auto rounded-lg border bg-muted/30 p-1">
        {TABS.map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-2 whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === key
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:bg-background/50 hover:text-foreground"
            }`}
          >
            {icon}
            {label}
          </button>
        ))}
      </div>

      <TabContent tab={activeTab} />
    </div>
  );
}
