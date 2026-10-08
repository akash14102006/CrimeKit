"use client";

import { Bell, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { roleLabel } from "@/hooks/useRBAC";
import { useDescope } from "@descope/react-sdk";
import { getUserInitials, getSafeDisplayName } from "@/lib/userDisplay";
import { ThemeToggle } from "./ThemeToggle";

export function Header() {
  const { user, clearSession } = useAuthStore();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const { logout: descopeLogout } = useDescope();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleLogout = () => {
    clearSession();
    try { descopeLogout(); } catch {}
    router.push("/login");
  };

  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6">
      <div className="flex flex-1 items-center">
        <form onSubmit={handleSearch} className="relative w-full max-w-md">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Global search across cases, evidence, and entities..."
            className="w-full bg-muted/50 pl-9 border-none focus-visible:ring-1"
          />
        </form>
      </div>
      <div className="flex items-center space-x-3">
        <ThemeToggle />
        <Button variant="ghost" size="icon" className="relative h-9 w-9" aria-label="Notifications">
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive" />
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger className="relative h-8 w-8 rounded-full focus:outline-none">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="bg-primary text-primary-foreground font-semibold text-xs">
                {getUserInitials(user?.name || user?.email)}
              </AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end">
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">
                  {getSafeDisplayName(user, "Investigator")}
                </p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user?.email || "user@crimekit.local"}
                </p>
                {user?.role && (
                  <p className="pt-1 text-xs leading-none text-muted-foreground capitalize">
                    {roleLabel(user.role)}
                  </p>
                )}
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onSelect={() => router.push("/settings")}>
              Profile Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem variant="destructive" onSelect={handleLogout}>
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
