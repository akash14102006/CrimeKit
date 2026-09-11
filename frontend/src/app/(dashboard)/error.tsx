"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { CircleAlert } from "lucide-react";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex h-full min-h-[60vh] w-full flex-col items-center justify-center gap-4 p-4 text-center">
      <CircleAlert className="h-10 w-10 text-destructive" aria-hidden="true" />
      <div className="space-y-1">
        <h2 className="text-xl font-bold tracking-tight">
          Something went wrong
        </h2>
        <p className="max-w-md text-sm text-muted-foreground">
          An error occurred while rendering this page. You can try again or
          return to the dashboard.
        </p>
      </div>
      <div className="flex gap-3">
        <Button onClick={() => reset()}>Try again</Button>
        <Button variant="outline" onClick={() => (window.location.href = "/dashboard")}>
          Go to Dashboard
        </Button>
      </div>
    </div>
  );
}
