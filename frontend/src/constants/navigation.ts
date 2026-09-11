import type { LucideIcon } from "lucide-react";
import type { Permission } from "@/types/auth";
import {
  Briefcase,
  CalendarClock,
  FileSearch,
  LayoutDashboard,
  Search,
  Settings,
  ShieldAlert,
  Workflow,
  Brain,
  Activity,
  FileText,
  Shield,
} from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  /** Permission required to view the item. */
  permission?: Permission;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

/** Primary navigation for the authenticated dashboard shell. */
export const NAV_SECTIONS: NavSection[] = [
  {
    title: "Overview",
    items: [
      {
        title: "Dashboard",
        href: "/dashboard",
        icon: LayoutDashboard,
      },
    ],
  },
  {
    title: "Investigation",
    items: [
      {
        title: "Cases",
        href: "/cases",
        icon: Briefcase,
        permission: "case:read",
      },
      {
        title: "Evidence Library",
        href: "/evidence",
        icon: FileSearch,
        permission: "evidence:read",
      },
      {
        title: "Search",
        href: "/search",
        icon: Search,
        permission: "search:query",
      },
    ],
  },
  {
    title: "Insights",
    items: [
      {
        title: "AI Workspace",
        href: "/ai",
        icon: Brain,
        permission: "kg:query",
      },
      {
        title: "Knowledge Graph",
        href: "/graph",
        icon: Workflow,
        permission: "kg:query",
      },
      {
        title: "Timeline",
        href: "/timeline",
        icon: CalendarClock,
        permission: "timeline:read",
      },
      {
        title: "Processing",
        href: "/processing",
        icon: Activity,
        permission: "case:read",
      },
    ],
  },
  {
    title: "Governance",
    items: [
      {
        title: "Reports",
        href: "/reports",
        icon: FileText,
        permission: "case:read",
      },
      {
        title: "Compliance",
        href: "/compliance",
        icon: Shield,
        permission: "case:read",
      },
      {
        title: "Admin",
        href: "/admin",
        icon: ShieldAlert,
        permission: "user:manage",
      },
      {
        title: "Settings",
        href: "/settings",
        icon: Settings,
      },
    ],
  },
];

export interface AppLink {
  label: string;
  href: string;
  external?: boolean;
}

/** Links shown on the marketing / auth landing page. */
export const PUBLIC_LINKS: AppLink[] = [
  { label: "Sign in", href: "/login" },
  { label: "Contact", href: "mailto:support@crimekit.io", external: true },
];
