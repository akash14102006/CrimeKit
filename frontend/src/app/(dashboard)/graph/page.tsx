import { Metadata } from "next";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { GraphPage } from "@/features/graph/components/GraphPage";

export const metadata: Metadata = {
  title: "Knowledge Graph - CrimeKit Enterprise",
};

export default function Page() {
  return (
    <AuthGuard allowedRoles={["admin", "investigator", "analyst", "viewer"]}>
      <GraphPage />
    </AuthGuard>
  );
}
