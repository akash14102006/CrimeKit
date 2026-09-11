"use client";

const LEGEND_ITEMS = [
  { color: "bg-blue-500", label: "Forensic Engine", source: "forensic_engine" },
  { color: "bg-purple-500", label: "Text Extraction", source: "text_extraction" },
  { color: "bg-cyan-500", label: "OCR", source: "ocr" },
  { color: "bg-emerald-500", label: "Evidence", source: "evidence" },
  { color: "bg-orange-500", label: "Processing", source: "processing" },
  { color: "bg-amber-500", label: "Custody", source: "custody" },
  { color: "bg-pink-500", label: "AI Analysis", source: "ai" },
  { color: "bg-gray-500", label: "System", source: "system" },
];

export function TimelineLegend() {
  return (
    <div className="flex items-center gap-3 flex-wrap px-1">
      {LEGEND_ITEMS.map((item) => (
        <div key={item.source} className="flex items-center gap-1.5">
          <div className={`h-2 w-2 rounded-full ${item.color}`} />
          <span className="text-[10px] text-muted-foreground">{item.label}</span>
        </div>
      ))}
    </div>
  );
}
