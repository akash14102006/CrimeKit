import { Metadata } from "next";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { AdminContent } from "./AdminContent";

export const metadata: Metadata = {
  title: "Administration - CrimeKit Enterprise",
};

export default function Page() {
  return (
    <AuthGuard allowedRoles={["admin"]}>
      <AdminContent />
    </AuthGuard>
  );
}
