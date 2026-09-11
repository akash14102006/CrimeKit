"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { X, Plus, Filter } from "lucide-react";
import { useSearchStore, type SearchFilter } from "../store/searchStore";

const FILTER_PRESETS: Omit<SearchFilter, "value">[] = [
  { key: "case_id", label: "Case ID", type: "text" },
  { key: "evidence_type", label: "Evidence Type", type: "select" },
  { key: "file_type", label: "File Type", type: "select" },
  { key: "date_from", label: "Date From", type: "date" },
  { key: "date_to", label: "Date To", type: "date" },
  { key: "entity_type", label: "Entity Type", type: "select" },
  { key: "priority", label: "Priority", type: "select" },
  { key: "status", label: "Status", type: "select" },
  { key: "processing_status", label: "Processing Status", type: "select" },
  { key: "has_ocr", label: "Has OCR Text", type: "boolean" },
  { key: "has_document", label: "Has Document", type: "boolean" },
];

const SELECT_OPTIONS: Record<string, string[]> = {
  evidence_type: ["image", "video", "pdf", "office", "email", "archive", "mobile_artifact", "disk_image", "browser_data", "unknown"],
  file_type: ["pdf", "docx", "xlsx", "jpg", "png", "mp4", "zip", "txt", "html", "eml"],
  entity_type: ["PERSON", "PHONE", "EMAIL", "DEVICE", "ACCOUNT", "LOCATION", "ORGANIZATION", "URL", "IP_ADDRESS"],
  priority: ["low", "medium", "high", "critical"],
  status: ["open", "in_progress", "closed", "archived"],
  processing_status: ["queued", "running", "completed", "failed"],
};

export function AdvancedFilters() {
  const { filters, addFilter, removeFilter, clearFilters, showFilters } =
    useSearchStore();
  const [addingFilter, setAddingFilter] = useState<string | null>(null);
  const [filterValue, setFilterValue] = useState("");

  const availableFilters = FILTER_PRESETS.filter(
    (fp) => !filters.find((f) => f.key === fp.key),
  );

  const handleAddFilter = useCallback(
    (preset: (typeof FILTER_PRESETS)[0]) => {
      if (preset.type === "boolean") {
        addFilter({ ...preset, value: "true" });
        setAddingFilter(null);
        return;
      }
      setAddingFilter(preset.key);
      setFilterValue("");
    },
    [addFilter],
  );

  const handleConfirmFilter = useCallback(() => {
    if (!addingFilter) return;
    const preset = FILTER_PRESETS.find((p) => p.key === addingFilter);
    if (!preset) return;

    if (filterValue.trim()) {
      addFilter({ ...preset, value: filterValue.trim() });
    }
    setAddingFilter(null);
    setFilterValue("");
  }, [addingFilter, filterValue, addFilter]);

  if (!showFilters) return null;

  return (
    <div className="border rounded-lg p-3 space-y-3 bg-muted/20">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="text-xs font-medium">Advanced Filters</span>
          {filters.length > 0 && (
            <Badge variant="secondary" className="text-[10px]">
              {filters.length}
            </Badge>
          )}
        </div>
        {filters.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 text-[10px]"
            onClick={clearFilters}
          >
            Clear All
          </Button>
        )}
      </div>

      {filters.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {filters.map((f) => (
            <Badge
              key={f.key}
              variant="outline"
              className="text-[10px] gap-1 pr-1"
            >
              <span className="text-muted-foreground">{f.label}:</span>
              <span className="font-medium">{String(f.value)}</span>
              <button
                className="ml-0.5 hover:text-destructive"
                onClick={() => removeFilter(f.key)}
              >
                <X className="h-2.5 w-2.5" />
              </button>
            </Badge>
          ))}
        </div>
      )}

      {addingFilter && (
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-muted-foreground">
            {FILTER_PRESETS.find((p) => p.key === addingFilter)?.label}:
          </span>
          {FILTER_PRESETS.find((p) => p.key === addingFilter)?.type === "select" ? (
            <select
              value={filterValue}
              onChange={(e) => setFilterValue(e.target.value)}
              className="h-7 text-xs flex-1 rounded-md border bg-transparent px-2"
            >
              <option value="">Select...</option>
              {(SELECT_OPTIONS[addingFilter] || []).map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          ) : (
            <Input
              value={filterValue}
              onChange={(e) => setFilterValue(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleConfirmFilter()}
              className="h-7 text-xs flex-1"
              placeholder="Enter value..."
              autoFocus
            />
          )}
          <Button
            size="sm"
            className="h-7 text-xs"
            onClick={handleConfirmFilter}
          >
            Add
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs"
            onClick={() => setAddingFilter(null)}
          >
            Cancel
          </Button>
        </div>
      )}

      {availableFilters.length > 0 && !addingFilter && (
        <div className="flex flex-wrap gap-1">
          {availableFilters.slice(0, 8).map((preset) => (
            <Button
              key={preset.key}
              variant="outline"
              size="sm"
              className="h-6 text-[10px] gap-1"
              onClick={() => handleAddFilter(preset)}
            >
              <Plus className="h-2.5 w-2.5" />
              {preset.label}
            </Button>
          ))}
        </div>
      )}
    </div>
  );
}
