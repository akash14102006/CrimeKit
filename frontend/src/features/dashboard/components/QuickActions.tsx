"use client";

import Link from "next/link";
import {
  Plus,
  Upload,
  Search,
  Briefcase,
  Brain,
  FileText,
  Users,
  Settings,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRBAC } from "@/hooks/useRBAC";
import type { Permission } from "@/types/auth";

interface QuickAction {
  label: string;
  href: string;
  icon: React.ReactNode;
  permission?: Permission;
}

const ACTIONS: QuickAction[] = [
  { label: "New Case", href: "/cases", icon: <Plus className="h-4 w-4" />, permission: "case:create" },
  { label: "Upload Evidence", href: "/evidence", icon: <Upload className="h-4 w-4" />, permission: "evidence:upload" },
  { label: "Search", href: "/search", icon: <Search className="h-4 w-4" /> },
  { label: "Open Workspace", href: "/cases", icon: <Briefcase className="h-4 w-4" />, permission: "case:read" },
  { label: "Knowledge Graph", href: "/graph", icon: <Brain className="h-4 w-4" />, permission: "kg:query" },
  { label: "View Reports", href: "/cases", icon: <FileText className="h-4 w-4" />, permission: "case:read" },
  { label: "Team", href: "/admin", icon: <Users className="h-4 w-4" />, permission: "user:manage" },
  { label: "Settings", href: "/settings", icon: <Settings className="h-4 w-4" /> },
];

export function QuickActions() {
  const { hasPermission } = useRBAC();

  const visibleActions = ACTIONS.filter(
    (a) => !a.permission || hasPermission(a.permission),
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Quick Actions</CardTitle>
        <CardDescription>Common investigation tasks</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {visibleActions.map((action) => (
            <Link key={action.label} href={action.href}>
              <Button
                variant="outline"
                className="w-full h-auto flex-col gap-2 py-4"
              >
                {action.icon}
                <span className="text-xs">{action.label}</span>
              </Button>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
