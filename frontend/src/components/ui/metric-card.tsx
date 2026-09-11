import type { LucideIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export interface MetricCardProps {
  title: string;
  value: React.ReactNode;
  icon?: LucideIcon;
  description?: React.ReactNode;
  tone?: "default" | "success" | "warning" | "destructive";
  className?: string;
}

const iconTones = {
  default: "text-muted-foreground",
  success: "text-success",
  warning: "text-warning",
  destructive: "text-destructive",
} as const;

export function MetricCard({
  title,
  value,
  icon: Icon,
  description,
  tone = "default",
  className,
}: MetricCardProps) {
  return (
    <Card className={cn("", className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {Icon && <Icon className={cn("h-4 w-4", iconTones[tone])} />}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}
