"use client";

import { memo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  FileText,
  RefreshCw,
  Copy,
  Download,
  Search,
  AlertTriangle,
  Info,
  AlertCircle,
} from "lucide-react";

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  processor?: string;
  stage?: string;
  worker?: string;
  duration_ms?: number;
}

export const ProcessingLogs = memo(function ProcessingLogs() {
  const [searchQuery, setSearchQuery] = useState("");
  const [levelFilter, setLevelFilter] = useState<string>("all");

  const logs: LogEntry[] = [];

  const filteredLogs = logs.filter((log) => {
    if (levelFilter !== "all" && log.level.toLowerCase() !== levelFilter) return false;
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const handleCopy = () => {
    const text = filteredLogs
      .map((l) => `[${l.timestamp}] [${l.level}] ${l.message}`)
      .join("\n");
    navigator.clipboard.writeText(text);
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <FileText className="h-4 w-4" />
          Processing Logs
        </CardTitle>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" className="h-7 text-[10px] gap-1" onClick={handleCopy}>
            <Copy className="h-3 w-3" />
            Copy
          </Button>
          <Button variant="ghost" size="sm" className="h-7 text-[10px] gap-1">
            <Download className="h-3 w-3" />
            Download
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 mb-3">
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <Search className="h-3 w-3 absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search logs..."
                className="h-7 text-xs pl-7"
              />
            </div>
            <div className="flex gap-1">
              {["all", "error", "warn", "info"].map((level) => (
                <Button
                  key={level}
                  variant={levelFilter === level ? "default" : "outline"}
                  size="sm"
                  className="h-6 text-[10px] capitalize"
                  onClick={() => setLevelFilter(level)}
                >
                  {level}
                </Button>
              ))}
            </div>
          </div>
        </div>

        <ScrollArea className="h-[300px]">
          {filteredLogs.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-6 w-6 mx-auto text-muted-foreground/30 mb-2" />
              <p className="text-xs text-muted-foreground">No logs available</p>
              <p className="text-[10px] text-muted-foreground">
                Logs will appear when processing jobs run
              </p>
            </div>
          ) : (
            <div className="space-y-1 font-mono text-[10px]">
              {filteredLogs.map((log, i) => (
                <div
                  key={`${log.timestamp}-${i}`}
                  className="flex items-start gap-2 py-1 px-2 rounded hover:bg-muted/30"
                >
                  <span className="text-muted-foreground shrink-0">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <Badge
                    variant="outline"
                    className={`text-[8px] shrink-0 ${
                      log.level === "error"
                        ? "text-red-600"
                        : log.level === "warn"
                          ? "text-amber-600"
                          : "text-blue-600"
                    }`}
                  >
                    {log.level === "error" ? (
                      <AlertCircle className="h-2 w-2 mr-0.5" />
                    ) : log.level === "warn" ? (
                      <AlertTriangle className="h-2 w-2 mr-0.5" />
                    ) : (
                      <Info className="h-2 w-2 mr-0.5" />
                    )}
                    {log.level}
                  </Badge>
                  <span className="flex-1 break-all">{log.message}</span>
                  {log.duration_ms !== undefined && (
                    <span className="text-muted-foreground shrink-0">
                      {log.duration_ms}ms
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
});
