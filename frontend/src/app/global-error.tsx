"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service if needed
    console.error(error);
  }, [error]);

  return (
    <html>
      <body>
        <div className="flex h-screen w-full flex-col items-center justify-center bg-background p-4 text-center">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-destructive/10 mb-6">
            <AlertTriangle className="h-10 w-10 text-destructive" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight mb-2">Something went wrong!</h2>
          <p className="text-muted-foreground mb-6 max-w-md">
            An unexpected error has occurred in the application. We have been notified and are looking into it.
          </p>
          <div className="flex gap-4">
            <Button onClick={() => reset()}>Try again</Button>
            <Button variant="outline" onClick={() => window.location.href = '/'}>Go Home</Button>
          </div>
        </div>
      </body>
    </html>
  );
}
