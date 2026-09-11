import { Metadata } from "next";
import { DiskAnalyzerPage } from "@/features/disk-analyzer/components/DiskAnalyzerPage";

export const metadata: Metadata = {
  title: "Disk Analyzer - CrimeKit Enterprise",
};

export function generateStaticParams() {
  return [{ evidenceId: "_" }];
}

export default function Page() {
  return <DiskAnalyzerPage />;
}
