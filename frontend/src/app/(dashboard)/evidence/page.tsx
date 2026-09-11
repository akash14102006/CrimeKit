import { Metadata } from "next";
import { EvidenceListPage } from "@/features/evidence/components/EvidenceListPage";

export const metadata: Metadata = {
  title: "Evidence Library - CrimeKit Enterprise",
};

export default function Page() {
  return <EvidenceListPage />;
}
