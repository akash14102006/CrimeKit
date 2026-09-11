import { Metadata } from "next";
import { CaseList } from "@/features/cases/components/CaseList";
import { AuthGuard } from "@/components/shared/AuthGuard";

export const metadata: Metadata = {
  title: "Case Management - CrimeKit Enterprise",
};

export default function Page() {
  return (
    <AuthGuard allowedRoles={['admin', 'investigator']}>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Case Management</h1>
          <p className="text-muted-foreground">
            Manage and track forensic investigations.
          </p>
        </div>
        <CaseList />
      </div>
    </AuthGuard>
  );
}
