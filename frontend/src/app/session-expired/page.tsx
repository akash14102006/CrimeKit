"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useSession, useDescope } from "@descope/react-sdk";
import { ShieldOff, ArrowLeft, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuthStore } from "@/store/authStore";

export default function SessionExpiredPage() {
  const router = useRouter();
  const { isAuthenticated } = useSession();
  const { logout: descopeLogout } = useDescope();
  const { clearSession } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, router]);

  function handleLogout() {
    clearSession();
    descopeLogout();
    router.push("/login");
  }

  return (
    <div className="flex min-h-[60vh] items-center justify-center p-4">
      <Card className="w-[440px] shadow-lg text-center">
        <CardHeader className="space-y-3">
          <div className="flex justify-center">
            <div className="h-16 w-16 rounded-full bg-destructive/10 flex items-center justify-center">
              <ShieldOff className="h-8 w-8 text-destructive" />
            </div>
          </div>
          <CardTitle className="text-xl">Session Expired</CardTitle>
          <CardDescription>
            Your session has timed out for security reasons. Please sign in again
            to continue.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground">
            All unsaved work may have been lost. If you were in the middle of an
            operation, you may need to start again.
          </p>
        </CardContent>
        <CardFooter className="flex flex-col gap-2 border-t p-4">
          <Button onClick={handleLogout} className="w-full gap-2">
            <RefreshCw className="h-4 w-4" />
            Sign In Again
          </Button>
          <Button render={<Link href="/dashboard" />} variant="ghost" className="w-full">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Return to Dashboard
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
