import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/shared/EmptyState";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex h-full min-h-[60vh] items-center justify-center">
      <EmptyState
        title="Page not found"
        description="The page you are looking for does not exist or has been moved."
        action={
          <Link href="/dashboard">
            <Button variant="outline" size="sm">
              Go to Dashboard
            </Button>
          </Link>
        }
      />
    </div>
  );
}
