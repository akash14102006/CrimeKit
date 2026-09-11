"use client";

import dynamic from "next/dynamic";
import { Shield } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const DescopeFlow = dynamic(
  () => import("@descope/react-sdk").then((m) => {
    const Descope = m.Descope;
    return function MfaDescope(props: React.ComponentProps<typeof Descope>) {
      return <Descope {...props} />;
    };
  }),
  { ssr: false },
);

export default function MfaPage() {
  const router = useRouter();

  return (
    <Card className="w-[420px] shadow-xl border-t-4 border-t-primary">
      <CardHeader className="space-y-1 text-center">
        <div className="flex justify-center mb-4">
          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Shield className="h-6 w-6 text-primary" />
          </div>
        </div>
        <CardTitle className="text-2xl tracking-tight">
          Multi-Factor Authentication
        </CardTitle>
        <CardDescription>
          Complete the verification step to continue
        </CardDescription>
      </CardHeader>
      <CardContent>
        <DescopeFlow
          flowId="mfa"
          onSuccess={() => {
            router.push("/dashboard");
          }}
          onError={(error) => {
            console.error("[CrimeKit] Descope MFA error:", error);
          }}
          theme="light"
        />
      </CardContent>
      <CardFooter className="flex justify-center border-t p-4 mt-4">
        <Button render={<Link href="/login" />} variant="ghost" className="w-full">
          Back to Login
        </Button>
      </CardFooter>
    </Card>
  );
}
