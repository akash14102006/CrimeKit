"use client";

import { UploadManager } from "./UploadManager";

interface EvidenceUploadModalProps {
  initialCaseId?: string;
}

export function EvidenceUploadModal({ initialCaseId }: EvidenceUploadModalProps) {
  return <UploadManager initialCaseId={initialCaseId} />;
}
