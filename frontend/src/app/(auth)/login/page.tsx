"use client";

import { useEffect } from "react";
import dynamic from "next/dynamic";

const LoginForm = dynamic(
  () => import("@/features/auth/components/LoginForm").then((m) => m.LoginForm),
  { ssr: false },
);

export default function LoginPage() {
  useEffect(() => {
    document.title = "Login - CrimeKit Enterprise";
  }, []);

  return <LoginForm />;
}
