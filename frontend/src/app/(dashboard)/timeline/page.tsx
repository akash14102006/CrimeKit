import { Metadata } from "next";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { TimelinePage } from "@/features/timeline/components/TimelinePage";

export const metadata: Metadata = {
  title: "Investigation Timeline - CrimeKit Enterprise",
};

export default function Page() {
  return (
    <AuthGuard allowedRoles={["admin", "investigator", "analyst", "viewer", "demo_evaluator", "jury_evaluator"]}>

      <TimelinePage />
    </AuthGuard>
  );
}
