import { WorkspaceLayout } from "@/features/workspace/components/WorkspaceLayout";
import { Metadata } from "next";
import { AuthGuard } from "@/components/shared/AuthGuard";

export const metadata: Metadata = {
  title: "Workspace - CrimeKit Enterprise",
};

export function generateStaticParams() {
  return [{ caseId: "_" }];
}

export default async function WorkspacePage({ params }: { params: Promise<{ caseId: string }> | { caseId: string } }) {
  const resolvedParams = await params;

  return (
    <AuthGuard allowedRoles={["admin", "investigator", "analyst", "viewer", "demo_evaluator", "jury_evaluator"]}>

      <WorkspaceLayout caseId={resolvedParams.caseId} />
    </AuthGuard>
  );
}
