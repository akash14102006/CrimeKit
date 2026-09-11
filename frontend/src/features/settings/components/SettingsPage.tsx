"use client";

import { useSettingsStore } from "../store/settingsStore";
import type { SettingsTab } from "../types/settings";
import { ProfilePanel } from "./ProfilePanel";
import { AppearancePanel } from "./AppearancePanel";
import { SecurityPanel } from "./SecurityPanel";
import { APIPreferencesPanel } from "./APIPreferencesPanel";
import { IntegrationsPanel } from "./IntegrationsPanel";
import {
  User,
  Palette,
  Shield,
  Key,
  Plug,
  Info,
} from "lucide-react";

const TABS: { key: SettingsTab; label: string; icon: React.ReactNode }[] = [
  { key: "profile", label: "Profile", icon: <User className="h-4 w-4" /> },
  { key: "appearance", label: "Appearance", icon: <Palette className="h-4 w-4" /> },
  { key: "security", label: "Security", icon: <Shield className="h-4 w-4" /> },
  { key: "api-keys", label: "API Keys", icon: <Key className="h-4 w-4" /> },
  { key: "integrations", label: "Integrations", icon: <Plug className="h-4 w-4" /> },
  { key: "about", label: "About", icon: <Info className="h-4 w-4" /> },
];

function AboutPanel() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">About CrimeKit</h2>
        <p className="text-sm text-muted-foreground">
          Enterprise digital forensics and investigation platform.
        </p>
      </div>
      <div className="rounded-lg border bg-card p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Platform:</span>
            <span className="ml-2 font-medium">CrimeKit Enterprise</span>
          </div>
          <div>
            <span className="text-muted-foreground">Version:</span>
            <span className="ml-2 font-mono text-xs">1.0.0</span>
          </div>
          <div>
            <span className="text-muted-foreground">Frontend:</span>
            <span className="ml-2">Next.js + React</span>
          </div>
          <div>
            <span className="text-muted-foreground">Backend:</span>
            <span className="ml-2">FastAPI + Python</span>
          </div>
          <div>
            <span className="text-muted-foreground">Auth:</span>
            <span className="ml-2">Descope</span>
          </div>
          <div>
            <span className="text-muted-foreground">Database:</span>
            <span className="ml-2">SQLite (dev)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function TabContent({ tab }: { tab: SettingsTab }) {
  switch (tab) {
    case "profile":
      return <ProfilePanel />;
    case "appearance":
      return <AppearancePanel />;
    case "security":
      return <SecurityPanel />;
    case "api-keys":
      return <APIPreferencesPanel />;
    case "integrations":
      return <IntegrationsPanel />;
    case "about":
      return <AboutPanel />;
    default:
      return <ProfilePanel />;
  }
}

export function SettingsPage() {
  const { activeTab, setActiveTab } = useSettingsStore();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account, preferences, and platform configuration.
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
