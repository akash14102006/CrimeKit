"use client";

import Link from "next/link";
import { ShieldAlert, ArrowLeft, Home } from "lucide-react";
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

export default function ForbiddenPage() {
  const { user } = useAuthStore();

  return (
    <div className="flex min-h-[60vh] items-center justify-center p-4">
      <Card className="w-[440px] shadow-lg text-center">
        <CardHeader className="space-y-3">
          <div className="flex justify-center">
            <div className="h-16 w-16 rounded-full bg-destructive/10 flex items-center justify-center">
              <ShieldAlert className="h-8 w-8 text-destructive" />
            </div>
          </div>
          <CardTitle className="text-xl">Access Denied</CardTitle>
          <CardDescription>
            You do not have permission to access this page.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Your current role
            {user?.role ? (
              <>
                {" "}
                (<span className="font-medium text-foreground">{user.role}</span>)
              </>
            ) : null}{" "}
            does not include the required permissions for this resource.
          </p>
          <p className="text-sm text-muted-foreground">
            Contact your organization administrator to request access.
          </p>
        </CardContent>
        <CardFooter className="flex flex-col gap-2 border-t p-4">
          <Button render={<Link href="/dashboard" />} className="w-full gap-2">
            <Home className="h-4 w-4" />
            Go to Dashboard
          </Button>
          <Button render={<Link href="/login" />} variant="ghost" className="w-full">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Sign In as Different User
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
