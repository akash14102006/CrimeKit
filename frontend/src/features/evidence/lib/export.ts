import type { Evidence } from "@/types/evidence";

export function exportEvidenceToCSV(items: Evidence[], filename = "evidence-export.csv") {
  const headers = [
    "ID",
    "Filename",
    "MIME Type",
    "Size (bytes)",
    "Case ID",
    "Uploaded By",
    "Upload Date",
    "SHA-256",
  ];

  const rows = items.map((item) => [
    item.id,
    item.filename,
    item.mime_type ?? "",
    String(item.size ?? 0),
    item.case_id ?? "",
    item.uploaded_by ?? "",
    item.uploaded_at ? new Date(item.uploaded_at).toISOString() : "",
    item.sha256 ?? "",
  ]);

  const csvContent = [
    headers.join(","),
    ...rows.map((row) =>
      row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","),
    ),
  ].join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
