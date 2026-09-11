"use client";

import { useState } from "react";
import { FileSearch, Clock, Users, RefreshCw, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useQuery } from "@tanstack/react-query";
import { evidenceService } from "@/services/evidenceService";
import { getErrorMessage } from "@/lib/api-client";

interface ForensicResultsResponse {
  evidence_id: string;
  results: Array<{
    id: string;
    processor: string;
    result: Record<string, unknown>;
    created_at?: string;
  }>;
  total: number;
}

interface TimelineResponse {
  evidence_id: string;
  timeline: Array<{
    timestamp?: string;
    date?: string;
    event?: string;
    description?: string;
    source_processor?: string;
    type?: string;
  }>;
  total: number;
}

interface EntitiesResponse {
  evidence_id: string;
  entities: Array<{
    type?: string;
    name?: string;
    value?: string;
    source_processor?: string;
    confidence?: number;
  }>;
  total: number;
}

interface FindingsResponse {
  evidence_id: string;
  findings: Array<{
    type?: string;
    severity?: string;
    message?: string;
    description?: string;
    source_processor?: string;
    confidence?: number;
    risk_level?: string;
  }>;
  total: number;
}

interface Props {
  evidenceId: string;
}

interface OcrResponse {
  evidence_id: string;
  text: string | null;
  source: string;
  metadata: Record<string, unknown>;
  created_at: string | null;
}

export function EvidenceForensicsCard({ evidenceId }: Props) {
  const [activeTab, setActiveTab] = useState("ocr");

  const { data: ocrData, isLoading: loadingOcr, error: ocrError } = useQuery({
    queryKey: ["evidence", evidenceId, "ocr"],
    queryFn: () => evidenceService.ocr(evidenceId),
    retry: 1,
    staleTime: 60_000,
  });

  const { data: resultsData, isLoading: loadingResults, refetch: refetchResults, error: resultsError } = useQuery<ForensicResultsResponse>({
    queryKey: ["advanced-forensics", "results", evidenceId],
    queryFn: () => evidenceService.advancedForensics.results(evidenceId),
    retry: 1,
  });

  const { data: timelineData, isLoading: loadingTimeline, refetch: refetchTimeline, error: timelineError } = useQuery<TimelineResponse>({
    queryKey: ["advanced-forensics", "timeline", evidenceId],
    queryFn: () => evidenceService.advancedForensics.timeline(evidenceId),
    retry: 1,
  });

  const { data: entitiesData, isLoading: loadingEntities, refetch: refetchEntities, error: entitiesError } = useQuery<EntitiesResponse>({
    queryKey: ["advanced-forensics", "entities", evidenceId],
    queryFn: () => evidenceService.advancedForensics.entities(evidenceId),
    retry: 1,
  });

  const { data: findingsData, isLoading: loadingFindings, refetch: refetchFindings, error: findingsError } = useQuery<FindingsResponse>({
    queryKey: ["advanced-forensics", "findings", evidenceId],
    queryFn: () => evidenceService.advancedForensics.findings(evidenceId),
    retry: 1,
  });

  const anyError = resultsError ?? timelineError ?? entitiesError ?? findingsError;
  const isLoadingAny = loadingResults || loadingTimeline || loadingEntities || loadingFindings;
  const hasData = (resultsData && resultsData.results.length > 0) || ocrData?.text;
  const ocrText = ocrData?.text ?? (resultsData?.results?.find(
    (r) => r.processor?.includes("ocr") || r.processor?.includes("text_extractor"),
  )?.result?.extracted_text as string | undefined) ?? undefined;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <FileSearch className="h-5 w-5" />
          OCR / Text Extraction & Forensic Analysis
        </CardTitle>
        <Button variant="outline" size="sm" onClick={() => { refetchResults(); refetchTimeline(); refetchEntities(); refetchFindings(); }} className="gap-1" disabled={isLoadingAny}>
          <RefreshCw className={`h-3.5 w-3.5 ${isLoadingAny ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </CardHeader>
      <CardContent>
        {anyError && hasData ? (
          <div className="text-center py-6">
            <AlertTriangle className="h-10 w-10 text-amber-500 mx-auto mb-3" />
            <p className="text-sm font-medium mb-1">Some forensic data failed to load</p>
            <p className="text-xs text-muted-foreground mb-3">
              {getErrorMessage(anyError, "One or more forensic endpoints returned an error.")}
            </p>
            <Button variant="outline" size="sm" onClick={() => { refetchResults(); refetchTimeline(); refetchEntities(); refetchFindings(); }} className="gap-1">
              <RefreshCw className="h-3.5 w-3.5" />
              Retry
            </Button>
          </div>
        ) : !hasData && !loadingOcr && !loadingResults ? (
          <div className="text-center py-6">
            <FileSearch className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground mb-3">
              {ocrData?.source === "none"
                ? "No OCR text has been extracted from this evidence yet. Run forensic processing to extract text."
                : "No forensic analysis data available."}
            </p>
            {ocrData?.source === "none" && (
              <p className="text-xs text-muted-foreground">
                Navigate to Processing to enqueue this evidence for forensic analysis.
              </p>
            )}
          </div>
        ) : (
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="ocr">OCR Text</TabsTrigger>
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
              <TabsTrigger value="entities">Entities</TabsTrigger>
              <TabsTrigger value="findings">Findings</TabsTrigger>
            </TabsList>

            <TabsContent value="ocr" className="mt-4">
              {loadingOcr || loadingResults ? (
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-4 w-full" />
                  ))}
                </div>
              ) : ocrText ? (
                <div className="bg-muted rounded-lg p-4 max-h-[300px] overflow-y-auto">
                  <pre className="text-xs font-mono whitespace-pre-wrap break-words">{ocrText}</pre>
                </div>
              ) : ocrData?.source === "none" ? (
                <div className="text-center py-4">
                  <FileSearch className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">No OCR text extracted yet.</p>
                  <p className="text-xs text-muted-foreground mt-1">Run forensic processing to extract text from this evidence.</p>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No OCR text extracted. The evidence may not contain extractable text.
                </p>
              )}
            </TabsContent>

            <TabsContent value="timeline" className="mt-4">
              {loadingTimeline ? (
                <div className="space-y-3">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex gap-3">
                      <Skeleton className="h-8 w-8 rounded-full shrink-0" />
                      <div className="flex-1 space-y-1">
                        <Skeleton className="h-4 w-[150px]" />
                        <Skeleton className="h-3 w-[200px]" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : timelineData?.timeline?.length ? (
                <div className="space-y-3 max-h-[300px] overflow-y-auto">
                  {timelineData.timeline.map((event, i) => (
                    <div key={i} className="flex gap-3 items-start">
                      <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium">{event.event || event.description || "Event"}</p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                          {event.timestamp && <span>{new Date(event.timestamp).toLocaleString()}</span>}
                          {event.date && <span>{event.date}</span>}
                          {event.source_processor && (
                            <Badge variant="outline" className="text-xs">{event.source_processor}</Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No timeline events found.
                </p>
              )}
            </TabsContent>

            <TabsContent value="entities" className="mt-4">
              {loadingEntities ? (
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-10 w-full" />
                  ))}
                </div>
              ) : entitiesData?.entities?.length ? (
                <div className="space-y-2 max-h-[300px] overflow-y-auto">
                  {entitiesData.entities.map((entity, i) => (
                    <div key={i} className="flex items-center justify-between p-2 border rounded-md">
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="text-sm font-medium">{entity.name || entity.value || "Unknown"}</p>
                          <p className="text-xs text-muted-foreground">{entity.type || "entity"}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {entity.confidence !== undefined && (
                          <Badge variant="outline" className="text-xs">
                            {Math.round(entity.confidence * 100)}%
                          </Badge>
                        )}
                        {entity.source_processor && (
                          <Badge variant="secondary" className="text-xs">
                            {entity.source_processor}
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No entities extracted.
                </p>
              )}
            </TabsContent>

            <TabsContent value="findings" className="mt-4">
              {loadingFindings ? (
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : findingsData?.findings?.length ? (
                <div className="space-y-2 max-h-[300px] overflow-y-auto">
                  {findingsData.findings.map((finding, i) => (
                    <div key={i} className="p-3 border rounded-md">
                      <div className="flex items-center justify-between mb-1">
                        <Badge
                          variant={
                            finding.severity === "high" || finding.risk_level === "high"
                              ? "destructive"
                              : finding.severity === "medium" || finding.risk_level === "medium"
                                ? "secondary"
                                : "outline"
                          }
                        >
                          {finding.severity || finding.risk_level || "info"}
                        </Badge>
                        {finding.source_processor && (
                          <Badge variant="outline" className="text-xs">
                            {finding.source_processor}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm mt-1">{finding.message || finding.description || "Finding"}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No findings detected.
                </p>
              )}
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
}
