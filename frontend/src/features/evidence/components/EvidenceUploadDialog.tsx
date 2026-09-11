"use client";

import { UploadManager } from "./UploadManager";

interface EvidenceUploadDialogProps {
  initialCaseId?: string;
}

export function EvidenceUploadDialog({ initialCaseId }: EvidenceUploadDialogProps) {
  return <UploadManager initialCaseId={initialCaseId} />;
}
