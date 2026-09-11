"use client";

import React from 'react';
import Link from 'next/link';
import { ShieldAlert, ArrowLeft, LogIn, Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export default function UnauthorizedPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-2xl border-t-4 border-t-destructive bg-card/95 backdrop-blur">
        <CardHeader className="space-y-2 text-center pb-2">
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 rounded-full bg-destructive/10 flex items-center justify-center ring-8 ring-destructive/5 animate-pulse">
              <ShieldAlert className="h-8 w-8 text-destructive" />
            </div>
          </div>
          <span className="text-xs font-mono tracking-widest text-destructive uppercase">Error 403</span>
          <CardTitle className="text-3xl font-bold tracking-tight">Access Denied</CardTitle>
          <CardDescription className="text-sm text-muted-foreground">
            You do not have the required RBAC permissions to view this resource.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 pt-4 text-center">
          <p className="text-xs text-muted-foreground bg-muted/50 p-3 rounded-lg border border-border/50">
            All unauthorized access attempts are logged and monitored by Enterprise Security Operations.
          </p>
        </CardContent>
        <CardFooter className="flex flex-col gap-2 pt-2">
          <Link href="/dashboard" className="w-full">
            <Button className="w-full gap-2">
              <ArrowLeft className="h-4 w-4" />
              Return to Dashboard
            </Button>
          </Link>
          <div className="grid grid-cols-2 gap-2 w-full">
            <Link href="/login" className="w-full">
              <Button variant="outline" className="w-full gap-2">
                <LogIn className="h-4 w-4" />
                Login Again
              </Button>
            </Link>
            <Button 
              variant="outline" 
              className="w-full gap-2"
              onClick={() => alert("Please contact your Security Administrator to request permission access.")}
            >
              <Mail className="h-4 w-4" />
              Contact Admin
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
