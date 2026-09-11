import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type StatusTone =
  | "default"
  | "secondary"
  | "success"
  | "warning"
  | "destructive"
  | "info";

const toneClass: Record<StatusTone, string> = {
  default: "",
  secondary: "border-transparent bg-secondary text-secondary-foreground",
  success:
    "border-transparent bg-success/15 text-success dark:bg-success/25",
  warning:
    "border-transparent bg-warning/15 text-warning dark:bg-warning/25",
  destructive: "border-transparent bg-destructive/15 text-destructive dark:bg-destructive/25",
  info: "border-transparent bg-primary/15 text-primary dark:bg-primary/25",
};

const statusTones: Record<string, StatusTone> = {
  active: "success",
  open: "success",
  ready: "success",
  completed: "success",
  running: "info",
  processing: "info",
  review: "warning",
  queued: "secondary",
  draft: "secondary",
  blocked: "destructive",
  failed: "destructive",
  closed: "secondary",
  cancelled: "secondary",
  degraded: "warning",
  unavailable: "destructive",
};

export interface StatusBadgeProps {
  status: string;
  className?: string;
}

/** Badge that maps a backend status string to a semantic color tone. */
export function StatusBadge({ status, className }: StatusBadgeProps) {
  const tone = statusTones[status.toLowerCase()] ?? "default";
  return (
    <Badge
      variant="outline"
      className={cn(toneClass[tone], "capitalize", className)}
    >
      {status}
    </Badge>
  );
}
