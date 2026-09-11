"use client";

import Link from "next/link";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DropdownMenuItem } from "@/components/ui/dropdown-menu";
import { useTSKCapabilities } from "@/features/disk-analyzer/hooks/useDiskAnalyzer";
import type { Evidence, ForensicImageMetadata } from "@/types/evidence";

interface Props {
  evidence: Evidence;
  variant?: "button" | "menu";
}

export function OpenDiskAnalyzerAction({ evidence, variant = "button" }: Props) {
  const { data: capabilities, isLoading } = useTSKCapabilities();
  const metadata = evidence.metadata as ForensicImageMetadata | null | undefined;
  const forensic = metadata?.forensic_image;
  const isForensicImage = metadata?.evidence_type === "forensic_disk_image";
  const capabilitySupported = metadata?.capability === "supported" || forensic?.capability === "supported";
  const ewfSupported = capabilities?.libewf_available || capabilities?.supported_image_formats?.includes("ewf_e01");

  if (!isForensicImage || !capabilitySupported || !ewfSupported || isLoading || !evidence.case_id) {
    return null;
  }

  if (variant === "menu") {
    return (
      <DropdownMenuItem
        render={<Link href={`/disk-analyzer/${evidence.id}`} />}
        className="gap-2"
      >
        <Search className="h-4 w-4" />
        Open Disk Analyzer
      </DropdownMenuItem>
    );
  }

  return (
    <Button render={<Link href={`/disk-analyzer/${evidence.id}`} />} size="sm" className="gap-1">
      <Search className="h-3.5 w-3.5" />
      Open Disk Analyzer
    </Button>
  );
}
