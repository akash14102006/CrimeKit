"use client";

import * as React from "react";
import { Moon, Sun, Laptop } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const subscribe = () => () => {};

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const mounted = React.useSyncExternalStore(subscribe, () => true, () => false);

  if (!mounted) {
    return (
      <Button variant="ghost" size="icon" className="h-9 w-9" aria-label="Toggle theme">
        <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      </Button>
    );
  }

  const isDark = resolvedTheme === "dark";

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        aria-label="Toggle application theme"
        className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-9 w-9 relative cursor-pointer"
      >
        {isDark ? (
          <Moon className="h-4 w-4 text-sky-400 transition-transform duration-200" />
        ) : (
          <Sun className="h-4 w-4 text-amber-500 transition-transform duration-200" />
        )}
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-36">
        <DropdownMenuItem onClick={() => setTheme("light")} className="gap-2 cursor-pointer text-xs">
          <Sun className="h-3.5 w-3.5 text-amber-500" />
          <span>Light</span>
          {theme === "light" && <span className="ml-auto text-[10px] text-sky-500 font-bold">✓</span>}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")} className="gap-2 cursor-pointer text-xs">
          <Moon className="h-3.5 w-3.5 text-sky-400" />
          <span>Dark</span>
          {theme === "dark" && <span className="ml-auto text-[10px] text-sky-500 font-bold">✓</span>}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")} className="gap-2 cursor-pointer text-xs">
          <Laptop className="h-3.5 w-3.5 text-slate-400" />
          <span>System</span>
          {theme === "system" && <span className="ml-auto text-[10px] text-sky-500 font-bold">✓</span>}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
