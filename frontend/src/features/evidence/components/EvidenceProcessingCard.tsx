"use client";

import { useState } from "react";
import { Cpu, Loader2, CheckCircle2, XCircle, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { API } from "@/constants/api-endpoints";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";

interface Props {
  evidenceId: string;
}

interface JobProgress {
  job_id: string;
  status: string;
  progress: number;
  queued_at?: string;
  started_at?: string;
  finished_at?: string;
  processors?: string[];
  completed_processors?: string[];
  error?: string;
}

export function EvidenceProcessingCard({ evidenceId }: Props) {
  const [lastEnqueuedJobId, setLastEnqueuedJobId] = useState<string | null>(null);

  const { data: processors } = useQuery({
    queryKey: ["processing", "processors"],
    queryFn: () => api.get<string[]>(API.processing.processors),
  });

  const { data: jobProgress } = useQuery<JobProgress>({
    queryKey: ["processing", "job", lastEnqueuedJobId],
    queryFn: () => api.get<JobProgress>(`/processing/jobs/${lastEnqueuedJobId}/progress`),
    enabled: !!lastEnqueuedJobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed" || status === "cancelled") {
        return false;
      }
      return 2000;
    },
  });

  const handleEnqueue = async () => {
    try {
      const result = await api.post<{ job_id: string }>(API.processing.enqueue(evidenceId), {
        processors: processors ?? ["metadata_extractor", "hash_verifier"],
      });
      setLastEnqueuedJobId(result.job_id);
      toast.add({
        title: "Processing Enqueued",
        description: "Evidence has been queued for forensic processing.",
        type: "success",
      });
    } catch (error) {
      toast.add({
        title: "Failed to Enqueue",
        description: getErrorMessage(error, "Could not enqueue evidence for processing."),
        type: "error",
      });
    }
  };

  const statusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "running":
      case "claiming":
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Processing Status</CardTitle>
        <Button variant="outline" size="sm" onClick={handleEnqueue} className="gap-1">
          <Cpu className="h-3.5 w-3.5" />
          Enqueue for Processing
        </Button>
      </CardHeader>
      <CardContent>
        {jobProgress ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              {statusIcon(jobProgress.status)}
              <Badge variant={jobProgress.status === "completed" ? "default" : jobProgress.status === "failed" ? "destructive" : "secondary"}>
                {jobProgress.status}
              </Badge>
              {jobProgress.progress > 0 && (
                <span className="text-sm text-muted-foreground">{jobProgress.progress}%</span>
              )}
            </div>
            {jobProgress.progress > 0 && (
              <Progress value={jobProgress.progress} className="h-2" />
            )}
            {jobProgress.completed_processors && jobProgress.completed_processors.length > 0 && (
              <div>
                <p className="text-xs font-medium mb-1">Completed:</p>
                <div className="flex flex-wrap gap-1">
                  {jobProgress.completed_processors.map((p) => (
                    <Badge key={p} variant="outline" className="text-xs">{p}</Badge>
                  ))}
                </div>
              </div>
            )}
            {jobProgress.error && (
              <p className="text-xs text-destructive">{jobProgress.error}</p>
            )}
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">
            <p>
              Use the button above to enqueue this evidence for automated forensic processing.
              Processors include metadata extraction, hash verification, and content analysis.
            </p>
            {processors && processors.length > 0 && (
              <div className="mt-3">
                <p className="text-xs font-medium mb-1">Available Processors:</p>
                <div className="flex flex-wrap gap-1">
                  {processors.map((p) => (
                    <Badge key={p} variant="outline" className="text-xs">
                      {p}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
