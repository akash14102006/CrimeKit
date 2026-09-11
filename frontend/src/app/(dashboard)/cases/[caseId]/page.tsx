import { Metadata } from "next";
import { CaseDetailPage } from "@/features/cases/components/CaseDetailPage";

export const metadata: Metadata = {
  title: "Case Details - CrimeKit Enterprise",
};

export function generateStaticParams() {
  return [{ caseId: "_" }];
}

export default async function Page({ params }: { params: Promise<{ caseId: string }> | { caseId: string } }) {
  const resolvedParams = await params;
  return <CaseDetailPage caseId={resolvedParams.caseId} />;
}
