import type { TimelineEvent } from "@/types/timeline";

function escapeCSV(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

export function exportTimelineToCSV(events: TimelineEvent[]): string {
  const headers = ["Timestamp", "Title", "Description", "Source", "Evidence ID", "Case ID"];
  const rows = events.map((e) => [
    escapeCSV(e.timestamp),
    escapeCSV(e.title),
    escapeCSV(e.description),
    escapeCSV(e.source),
    escapeCSV(e.evidence_id ?? ""),
    escapeCSV(e.case_id ?? ""),
  ]);
  return [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
}

export function exportTimelineToJSON(events: TimelineEvent[]): string {
  return JSON.stringify(events, null, 2);
}

export function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
