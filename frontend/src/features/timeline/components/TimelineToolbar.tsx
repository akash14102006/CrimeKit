"use client";

import { useState, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Search,
  X,
  ZoomIn,
  ZoomOut,
  LayoutList,
  AlignJustify,
  Rows3,
  Download,
  Calendar,
  Filter,
  RefreshCw,
} from "lucide-react";
import { useTimelineStore, type TimelineMode, type TimelineZoom } from "../store/timelineStore";
import { exportTimelineToCSV, exportTimelineToJSON, downloadFile } from "../lib/export";
import type { TimelineEvent } from "@/types/timeline";

const SOURCE_FILTERS = [
  { value: "all", label: "All Sources" },
  { value: "forensic_engine", label: "Forensic Engine" },
  { value: "text_extraction", label: "Text Extraction" },
  { value: "ocr", label: "OCR" },
  { value: "evidence", label: "Evidence" },
  { value: "processing", label: "Processing" },
  { value: "custody", label: "Custody" },
  { value: "ai", label: "AI Analysis" },
  { value: "system", label: "System" },
];

const ZOOM_LEVELS: { value: TimelineZoom; label: string }[] = [
  { value: "minutes", label: "Minutes" },
  { value: "hours", label: "Hours" },
  { value: "days", label: "Days" },
  { value: "weeks", label: "Weeks" },
  { value: "months", label: "Months" },
];

const MODE_OPTIONS: { value: TimelineMode; label: string; icon: typeof LayoutList }[] = [
  { value: "vertical", label: "Vertical", icon: LayoutList },
  { value: "compact", label: "Compact", icon: Rows3 },
  { value: "grouped", label: "Grouped", icon: AlignJustify },
];

interface Props {
  events: TimelineEvent[];
  isLoading: boolean;
  onRefresh: () => void;
}

export function TimelineToolbar({ events, isLoading, onRefresh }: Props) {
  const {
    searchQuery, setSearchQuery,
    sourceFilter, setSourceFilter,
    zoom, setZoom,
    mode, setMode,
    dateFrom, setDateFrom,
    dateTo, setDateTo,
  } = useTimelineStore();

  const [showDateFilter, setShowDateFilter] = useState(false);

  const activeZoomIndex = ZOOM_LEVELS.findIndex((z) => z.value === zoom);

  const handleZoomIn = useCallback(() => {
    if (activeZoomIndex > 0) setZoom(ZOOM_LEVELS[activeZoomIndex - 1].value);
  }, [activeZoomIndex, setZoom]);

  const handleZoomOut = useCallback(() => {
    if (activeZoomIndex < ZOOM_LEVELS.length - 1) setZoom(ZOOM_LEVELS[activeZoomIndex + 1].value);
  }, [activeZoomIndex, setZoom]);

  const handleExportCSV = useCallback(() => {
    const csv = exportTimelineToCSV(events);
    downloadFile(csv, `timeline-export-${new Date().toISOString().slice(0, 10)}.csv`, "text/csv");
  }, [events]);

  const handleExportJSON = useCallback(() => {
    const json = exportTimelineToJSON(events);
    downloadFile(json, `timeline-export-${new Date().toISOString().slice(0, 10)}.json`, "application/json");
  }, [events]);

  const hasActiveFilters = sourceFilter !== "all" || dateFrom || dateTo;

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <div className="relative flex-1 min-w-[200px] max-w-md">
        <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
        <Input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search timeline events..."
          className="h-8 pl-8 pr-8 text-xs"
        />
        {searchQuery && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-1 top-1 h-6 w-6 p-0"
            onClick={() => setSearchQuery("")}
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>

      <div className="flex items-center gap-1 border rounded-md">
        <Button variant="ghost" size="sm" className="h-7 px-2" onClick={handleZoomIn} disabled={activeZoomIndex <= 0}>
          <ZoomIn className="h-3.5 w-3.5" />
        </Button>
        <span className="text-[10px] font-medium text-muted-foreground px-1 min-w-[40px] text-center">
          {ZOOM_LEVELS.find((z) => z.value === zoom)?.label}
        </span>
        <Button variant="ghost" size="sm" className="h-7 px-2" onClick={handleZoomOut} disabled={activeZoomIndex >= ZOOM_LEVELS.length - 1}>
          <ZoomOut className="h-3.5 w-3.5" />
        </Button>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger className="inline-flex items-center gap-1 h-7 px-2 text-xs font-medium rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground">
              <Filter className="h-3 w-3" />
              {SOURCE_FILTERS.find((s) => s.value === sourceFilter)?.label ?? "Filter"}
            </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          {SOURCE_FILTERS.map((filter) => (
            <DropdownMenuItem key={filter.value} onClick={() => setSourceFilter(filter.value)}>
              {filter.label}
              {sourceFilter === filter.value && <Badge variant="secondary" className="ml-2 text-[10px]">Active</Badge>}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <Button
        variant={showDateFilter ? "default" : "outline"}
        size="sm"
        className="h-7 gap-1"
        onClick={() => setShowDateFilter(!showDateFilter)}
      >
        <Calendar className="h-3 w-3" />
        Date Range
      </Button>

      {showDateFilter && (
        <div className="flex items-center gap-1">
          <Input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="h-7 w-[130px] text-[10px]"
          />
          <span className="text-[10px] text-muted-foreground">to</span>
          <Input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="h-7 w-[130px] text-[10px]"
          />
        </div>
      )}

      <div className="flex items-center border rounded-md">
        {MODE_OPTIONS.map((opt) => {
          const Icon = opt.icon;
          return (
            <Button
              key={opt.value}
              variant={mode === opt.value ? "default" : "ghost"}
              size="sm"
              className="h-7 px-2 rounded-none"
              onClick={() => setMode(opt.value)}
            >
              <Icon className="h-3.5 w-3.5" />
            </Button>
          );
        })}
      </div>

      <div className="flex items-center gap-1">
        <Button variant="outline" size="sm" className="h-7" onClick={onRefresh} disabled={isLoading}>
          <RefreshCw className={`h-3 w-3 ${isLoading ? "animate-spin" : ""}`} />
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger className="inline-flex items-center gap-1 h-7 px-2 text-xs font-medium rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground">
              <Download className="h-3 w-3" />
              Export
            </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={handleExportCSV}>Export as CSV</DropdownMenuItem>
            <DropdownMenuItem onClick={handleExportJSON}>Export as JSON</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {hasActiveFilters && (
        <Button variant="ghost" size="sm" className="h-7 text-[10px]" onClick={() => { setSourceFilter("all"); setDateFrom(""); setDateTo(""); }}>
          Clear filters
        </Button>
      )}

      <div className="flex-1" />

      <Badge variant="outline" className="text-[10px]">
        {events.length} event{events.length !== 1 ? "s" : ""}
      </Badge>
    </div>
  );
}
