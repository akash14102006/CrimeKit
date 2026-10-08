import { cn } from "@/lib/utils";
import { IsometricLoader } from "./IsometricLoader";

interface LoadingStateProps {
  label?: string;
  className?: string;
}

export function LoadingState({ label = "Loading...", className }: LoadingStateProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        "flex flex-col items-center justify-center gap-4 p-8 text-muted-foreground min-h-[240px]",
        className,
      )}
    >
      <IsometricLoader size={32} />
      {label && <p className="text-xs font-mono text-muted-foreground tracking-wider uppercase">{label}</p>}
    </div>
  );
}
