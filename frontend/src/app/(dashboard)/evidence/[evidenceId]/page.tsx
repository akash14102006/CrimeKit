import { Metadata } from "next";
import { EvidenceDetailPage } from "@/features/evidence/components/EvidenceDetailPage";

export const metadata: Metadata = {
  title: "Evidence Details - CrimeKit Enterprise",
};

export function generateStaticParams() {
  return [{ evidenceId: "_" }];
}

export default function Page() {
  return <EvidenceDetailPage />;
}
