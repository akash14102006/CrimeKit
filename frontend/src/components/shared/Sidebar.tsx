"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/authStore";
import { NAV_SECTIONS } from "@/constants/navigation";
import { useRBAC } from "@/hooks/useRBAC";
import { useDescope } from "@descope/react-sdk";

export function Sidebar() {
  const pathname = usePathname();
  const { clearSession } = useAuthStore();
  const { hasPermission } = useRBAC();
  const { logout: descopeLogout } = useDescope();

  const handleLogout = () => {
    clearSession();
    descopeLogout();
    window.location.href = "/login";
  };

  return (
    <div className="flex h-full w-64 flex-col bg-sidebar border-r border-sidebar-border text-sidebar-foreground transition-all duration-300">
      <div className="flex h-16 items-center border-b border-sidebar-border px-6">
        <Image
          src="/crimekit-logo.png"
          alt="CrimeKit"
          width={24}
          height={24}
          className="mr-3 h-6 w-6 object-contain"
          priority
        />
        <span className="text-lg font-bold tracking-tight">CrimeKit</span>
      </div>
      <div className="flex-1 overflow-y-auto py-4">
        {NAV_SECTIONS.map((section) => {
          const visibleItems = section.items.filter(
            (item) => !item.permission || hasPermission(item.permission),
          );
          if (visibleItems.length === 0) return null;
          return (
            <div key={section.title} className="mb-4">
              <p className="px-6 pb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {section.title}
              </p>
              <nav className="space-y-1 px-3">
                {visibleItems.map((item) => {
                  const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      aria-current={isActive ? "page" : undefined}
                      className={cn(
                        "flex items-center rounded-md px-3 py-2.5 text-sm font-medium transition-colors",
                        isActive
                          ? "bg-sidebar-accent text-sidebar-accent-foreground"
                          : "text-sidebar-foreground hover:bg-muted hover:text-foreground"
                      )}
                    >
                      <item.icon
                        className={cn(
                          "mr-3 h-5 w-5 flex-shrink-0",
                          isActive
                            ? "text-sidebar-accent-foreground"
                            : "text-muted-foreground"
                        )}
                      />
                      {item.title}
                    </Link>
                  );
                })}
              </nav>
            </div>
          );
        })}
      </div>
      <div className="border-t border-sidebar-border p-4">
        <Button
          variant="ghost"
          className="w-full justify-start text-muted-foreground hover:text-foreground"
          onClick={handleLogout}
        >
          <LogOut className="mr-3 h-5 w-5" />
          Sign out
        </Button>
      </div>
    </div>
  );
}
