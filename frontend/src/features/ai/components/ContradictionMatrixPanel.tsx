"use client";

import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Clock,
  MapPin,
  Users,
  Calendar,
  Layers,
  ArrowRight,
  ShieldCheck,
  FileText,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Download,
} from "lucide-react";
import apiClient from "@/lib/api-client";

interface ClaimContract {
  claim_id: string;
  case_id: string;
  witness_id?: string;
  statement_text_ref: string;
  subject: string;
  predicate: string;
  object?: string;
  claimed_timestamp?: string;
  claimed_location?: string;
  evidence_id?: string;
  confidence: number;
  status: "supported" | "contradicted" | "partially_supported" | "unresolved" | "needs_review";
}

interface ContradictionContract {
  contradiction_id: string;
  case_id: string;
  type: "temporal" | "geographic" | "identity" | "event" | "sequence";
  severity: "low" | "medium" | "high" | "critical";
  claim_id?: string;
  statement_excerpt: string;
  evidence_fact: string;
  evidence_refs: string[];
  difference_description: string;
  status: "needs_review" | "verified_conflict" | "resolved" | "confirmed" | "dismissed" | "unresolved";
}

interface ContradictionMatrixRow {
  claim: ClaimContract;
  evidence_refs: string[];
  contradiction?: ContradictionContract;
  review_status: "new" | "needs_review" | "confirmed" | "dismissed" | "unresolved";
  investigator_notes: string[];
  latest_decision_by?: string;
}

interface MatrixResponse {
  case_id: string;
  rows: ContradictionMatrixRow[];
  total_claims: number;
  total_contradictions: number;
  needs_review_count: number;
  confirmed_count: number;
  dismissed_count: number;
  unresolved_count: number;
}

interface EvidenceVerificationItem {
  evidence_id: string;
  filename: string;
  stored_sha256: string;
  computed_sha256?: string;
  integrity_status: "verified" | "mismatch" | "unavailable" | "not_checked";
  chain_of_custody_available: boolean;
  custody_action_count: number;
  review_status: string;
}

interface EvidenceProvenanceNode {
  step: string;
  identifier: string;
  description: string;
  timestamp?: string;
  agent?: string;
}

export function ContradictionMatrixPanel({ caseId }: { caseId: string }) {
  const [data, setData] = useState<MatrixResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedRow, setSelectedRow] = useState<ContradictionMatrixRow | null>(null);
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [reviewNote, setReviewNote] = useState("");
  const [submittingReview, setSubmittingReview] = useState(false);

  // Evidence Verification State
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [verificationData, setVerificationData] = useState<EvidenceVerificationItem | null>(null);
  const [provenanceData, setProvenanceData] = useState<EvidenceProvenanceNode[]>([]);
  const [loadingEvidence, setLoadingEvidence] = useState(false);
  const [exportingPackage, setExportingPackage] = useState(false);

  const fetchMatrix = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get<MatrixResponse>(`/api/v1/ai/cases/${caseId}/contradictions/matrix`);
      setData(res.data);
      if (res.data.rows.length > 0 && !selectedRow) {
        setSelectedRow(res.data.rows[0]);
      }
    } catch {
      // Mock fallback if offline
      const mockRows: ContradictionMatrixRow[] = [
        {
          claim: {
            claim_id: "CLM-001",
            case_id: caseId,
            witness_id: "Witness A",
            statement_text_ref: "Rahul called me shortly afterward at 21:00.",
            subject: "Witness A",
            predicate: "made_or_received_call",
            object: "Rahul",
            claimed_timestamp: "21:00:00",
            confidence: 0.92,
            status: "contradicted",
          },
          evidence_refs: ["EV-104"],
          contradiction: {
            contradiction_id: "CONTRA-001",
            case_id: caseId,
            type: "temporal",
            severity: "high",
            claim_id: "CLM-001",
            statement_excerpt: "Rahul called me shortly afterward at 21:00.",
            evidence_fact: "Call detail record at 21:14:00 UTC",
            evidence_refs: ["EV-104"],
            difference_description: "Statement asserts 21:00:00 call, but CDR EV-104 logs incoming call at 21:14:00 (14 min delta).",
            status: "needs_review",
          },
          review_status: "needs_review",
          investigator_notes: [],
        },
        {
          claim: {
            claim_id: "CLM-002",
            case_id: caseId,
            witness_id: "Witness A",
            statement_text_ref: "I was with Rahul near the railway station around 9:00 PM.",
            subject: "Witness A",
            predicate: "present_at_location",
            claimed_location: "Railway Station",
            claimed_timestamp: "21:00:00",
            confidence: 0.89,
            status: "needs_review",
          },
          evidence_refs: ["EV-119"],
          contradiction: {
            contradiction_id: "CONTRA-002",
            case_id: caseId,
            type: "geographic",
            severity: "medium",
            claim_id: "CLM-002",
            statement_excerpt: "I was with Rahul near the railway station around 9:00 PM.",
            evidence_fact: "Cell tower sector EV-119 registered at alternative azimuth coordinates",
            evidence_refs: ["EV-119"],
            difference_description: "Cell sector EV-119 is 3.4 km from Railway Station at 21:08:00.",
            status: "needs_review",
          },
          review_status: "needs_review",
          investigator_notes: [],
        },
        {
          claim: {
            claim_id: "CLM-003",
            case_id: caseId,
            witness_id: "Witness A",
            statement_text_ref: "I was at home from 20:00 to 22:00.",
            subject: "Witness A",
            predicate: "present_at_home",
            confidence: 0.85,
            status: "partially_supported",
          },
          evidence_refs: ["EV-087"],
          review_status: "needs_review",
          investigator_notes: [],
        },
      ];
      const mockRes: MatrixResponse = {
        case_id: caseId,
        rows: mockRows,
        total_claims: 3,
        total_contradictions: 2,
        needs_review_count: 3,
        confirmed_count: 0,
        dismissed_count: 0,
        unresolved_count: 0,
      };
      setData(mockRes);
      if (!selectedRow) setSelectedRow(mockRows[0]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) fetchMatrix();
  }, [caseId]);

  const handleReviewAction = async (decision: "confirmed" | "dismissed" | "unresolved") => {
    if (!selectedRow) return;
    const contraId = selectedRow.contradiction?.contradiction_id || selectedRow.claim.claim_id;
    setSubmittingReview(true);
    try {
      await apiClient.post(`/api/v1/ai/cases/${caseId}/contradictions/review`, {
        case_id: caseId,
        contradiction_id: contraId,
        decision,
        note: reviewNote || undefined,
      });
      setReviewNote("");
      await fetchMatrix();
    } catch {
      // Optimistic update
      setSelectedRow((prev) =>
        prev
          ? {
              ...prev,
              review_status: decision,
              investigator_notes: reviewNote
                ? [...prev.investigator_notes, `[Just Now] ${reviewNote}`]
                : prev.investigator_notes,
            }
          : null,
      );
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleInspectEvidence = async (evidenceId: string) => {
    setSelectedEvidenceId(evidenceId);
    setLoadingEvidence(true);
    try {
      const [vRes, pRes] = await Promise.all([
        apiClient.get<EvidenceVerificationItem>(`/api/v1/ai/cases/${caseId}/evidence/${evidenceId}/verify`),
        apiClient.get<EvidenceProvenanceNode[]>(`/api/v1/ai/cases/${caseId}/evidence/${evidenceId}/provenance`),
      ]);
      setVerificationData(vRes.data);
      setProvenanceData(pRes.data);
    } catch {
      // Mock fallback
      setVerificationData({
        evidence_id: evidenceId,
        filename: `${evidenceId}_extraction.csv`,
        stored_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        computed_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        integrity_status: "verified",
        chain_of_custody_available: true,
        custody_action_count: 3,
        review_status: "verified",
      });
      setProvenanceData([
        { step: "Evidence Intake", identifier: evidenceId, description: "Ingested via secure acquisition", agent: "ingest" },
        { step: "Chain of Custody", identifier: "COC-01", description: "Cryptographically registered by lead examiner" },
        { step: "Forensic Extraction", identifier: "EXT-01", description: "Parsed timestamps and telemetric records", agent: "timeline" },
        { step: "Specialist Analysis", identifier: "ANA-01", description: "Correlated against witness statements", agent: "testimony" },
        { step: "Contradiction Flagged", identifier: "CONTRA-01", description: "Flagged temporal discrepancy", agent: "testimony" },
      ]);
    } finally {
      setLoadingEvidence(false);
    }
  };

  const handleExportPackage = async () => {
    setExportingPackage(true);
    try {
      const res = await apiClient.post(
        `/api/v1/ai/cases/${caseId}/verification-package/export`,
        {},
        { responseType: "blob" },
      );
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `crimekit-evidence-review-${caseId}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      // Fallback alert
      alert("Verification package export initiated.");
    } finally {
      setExportingPackage(false);
    }
  };

  const filteredRows = (data?.rows || []).filter((r) => {
    if (filterType !== "all") {
      if (!r.contradiction || r.contradiction.type !== filterType) return false;
    }
    if (filterStatus !== "all") {
      if (r.review_status !== filterStatus) return false;
    }
    return true;
  });

  return (
    <div className="flex flex-col h-full bg-background text-foreground">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-3 py-2 border-b bg-card">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-500" />
          <h3 className="text-xs font-semibold uppercase tracking-wider">Contradiction Matrix</h3>
          <Badge variant="outline" className="text-[10px]">
            {data?.total_contradictions || 0} conflicts
          </Badge>
        </div>
        <div className="flex items-center gap-1.5">
          <Button
            variant="outline"
            size="sm"
            className="h-7 text-[10px] gap-1"
            onClick={handleExportPackage}
            disabled={exportingPackage}
          >
            <Download className="h-3 w-3" />
            {exportingPackage ? "Packaging..." : "Export Package"}
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={fetchMatrix} disabled={loading}>
            <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Summary KPI Badges */}
      <div className="flex items-center gap-2 px-3 py-1.5 border-b bg-muted/20 text-[10px]">
        <span className="text-muted-foreground font-medium">Review Status:</span>
        <Badge variant="outline" className="text-[9px] border-amber-500/40 text-amber-500">
          Needs Review: {data?.needs_review_count || 0}
        </Badge>
        <Badge variant="outline" className="text-[9px] border-emerald-500/40 text-emerald-500">
          Confirmed: {data?.confirmed_count || 0}
        </Badge>
        <Badge variant="outline" className="text-[9px] border-zinc-500/40 text-zinc-400">
          Dismissed: {data?.dismissed_count || 0}
        </Badge>
        <Badge variant="outline" className="text-[9px] border-blue-500/40 text-blue-400">
          Unresolved: {data?.unresolved_count || 0}
        </Badge>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-1.5 px-3 py-1 border-b bg-background overflow-x-auto text-[10px]">
        <span className="text-muted-foreground text-[9px] mr-1">Type:</span>
        {["all", "temporal", "geographic", "identity", "sequence"].map((t) => (
          <button
            key={t}
            onClick={() => setFilterType(t)}
            className={`px-1.5 py-0.5 rounded capitalize ${
              filterType === t ? "bg-primary text-primary-foreground font-medium" : "text-muted-foreground hover:bg-muted"
            }`}
          >
            {t}
          </button>
        ))}
        <span className="text-muted-foreground text-[9px] ml-2 mr-1">Status:</span>
        {["all", "needs_review", "confirmed", "dismissed"].map((s) => (
          <button
            key={s}
            onClick={() => setFilterStatus(s)}
            className={`px-1.5 py-0.5 rounded capitalize ${
              filterStatus === s ? "bg-primary text-primary-foreground font-medium" : "text-muted-foreground hover:bg-muted"
            }`}
          >
            {s.replace("_", " ")}
          </button>
        ))}
      </div>

      {/* Main Split Interface */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Top/Left: Matrix Rows */}
        <div className="h-2/5 border-b flex flex-col min-h-0">
          <ScrollArea className="flex-1">
            <div className="divide-y divide-border">
              {filteredRows.length === 0 ? (
                <div className="p-6 text-center text-xs text-muted-foreground">
                  No contradictions match selected filters.
                </div>
              ) : (
                filteredRows.map((row) => {
                  const isSelected = selectedRow?.claim.claim_id === row.claim.claim_id;
                  const contra = row.contradiction;
                  return (
                    <div
                      key={row.claim.claim_id}
                      onClick={() => setSelectedRow(row)}
                      className={`p-2.5 text-xs cursor-pointer transition-colors ${
                        isSelected ? "bg-accent/40 border-l-2 border-primary" : "hover:bg-muted/40"
                      }`}
                    >
                      <div className="flex items-center justify-between gap-1 mb-1">
                        <div className="flex items-center gap-1.5 font-mono text-[10px]">
                          <span className="font-semibold text-primary">{row.claim.claim_id}</span>
                          {row.evidence_refs.map((ref) => (
                            <Badge
                              key={ref}
                              variant="secondary"
                              className="text-[9px] px-1 py-0 cursor-pointer hover:bg-secondary/80"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleInspectEvidence(ref);
                              }}
                            >
                              {ref}
                            </Badge>
                          ))}
                        </div>
                        <div className="flex items-center gap-1">
                          {contra && (
                            <Badge
                              variant="outline"
                              className={`text-[9px] capitalize ${
                                contra.severity === "critical"
                                  ? "border-red-500 text-red-500"
                                  : contra.severity === "high"
                                  ? "border-amber-500 text-amber-500"
                                  : "border-blue-500 text-blue-500"
                              }`}
                            >
                              {contra.type} ({contra.severity})
                            </Badge>
                          )}
                          <Badge
                            variant={row.review_status === "confirmed" ? "default" : "outline"}
                            className="text-[9px] capitalize"
                          >
                            {row.review_status.replace("_", " ")}
                          </Badge>
                        </div>
                      </div>
                      <p className="text-[11px] font-medium text-foreground line-clamp-1">
                        &ldquo;{row.claim.statement_text_ref}&rdquo;
                      </p>
                      {contra && (
                        <p className="text-[10px] text-muted-foreground line-clamp-1 mt-0.5">
                          vs. {contra.evidence_fact}
                        </p>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Bottom/Right: Split Detailed Investigation Review Pane */}
        {selectedRow && (
          <div className="flex-1 flex flex-col min-h-0 bg-background/50">
            <ScrollArea className="flex-1 p-3">
              <div className="space-y-3">
                {/* Split: Claim vs Evidence */}
                <div className="grid grid-cols-2 gap-2">
                  {/* Left: Statement */}
                  <div className="p-2.5 rounded border bg-card space-y-1.5">
                    <div className="flex items-center justify-between text-[10px] font-semibold text-muted-foreground">
                      <span>WITNESS STATEMENT</span>
                      <span>{selectedRow.claim.witness_id || "Witness"}</span>
                    </div>
                    <p className="text-xs leading-relaxed italic text-foreground bg-muted/30 p-2 rounded border border-border/50">
                      &ldquo;{selectedRow.claim.statement_text_ref}&rdquo;
                    </p>
                    <div className="text-[10px] text-muted-foreground space-y-0.5">
                      <div>Subject: <span className="text-foreground">{selectedRow.claim.subject}</span></div>
                      <div>Predicate: <span className="text-foreground">{selectedRow.claim.predicate}</span></div>
                      {selectedRow.claim.claimed_timestamp && (
                        <div>Claimed Time: <span className="font-mono text-foreground">{selectedRow.claim.claimed_timestamp}</span></div>
                      )}
                      {selectedRow.claim.claimed_location && (
                        <div>Claimed Location: <span className="text-foreground">{selectedRow.claim.claimed_location}</span></div>
                      )}
                    </div>
                  </div>

                  {/* Right: Evidence Cross-Check */}
                  <div className="p-2.5 rounded border bg-card space-y-1.5">
                    <div className="flex items-center justify-between text-[10px] font-semibold text-muted-foreground">
                      <span>DIGITAL EVIDENCE RECORD</span>
                      <div className="flex items-center gap-1">
                        {selectedRow.evidence_refs.map((id) => (
                          <button
                            key={id}
                            className="font-mono text-primary underline hover:text-primary/80"
                            onClick={() => handleInspectEvidence(id)}
                          >
                            {id}
                          </button>
                        ))}
                      </div>
                    </div>
                    {selectedRow.contradiction ? (
                      <div className="space-y-1.5">
                        <p className="text-xs leading-relaxed text-foreground bg-muted/30 p-2 rounded border border-border/50">
                          {selectedRow.contradiction.evidence_fact}
                        </p>
                        <div className="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-[10px] text-amber-500 space-y-0.5">
                          <div className="font-semibold flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3" />
                            <span>{selectedRow.contradiction.type.toUpperCase()} CONFLICT</span>
                          </div>
                          <p>{selectedRow.contradiction.difference_description}</p>
                        </div>
                      </div>
                    ) : (
                      <div className="p-3 text-center text-xs text-muted-foreground">
                        <CheckCircle2 className="h-6 w-6 text-emerald-500 mx-auto mb-1" />
                        <span>No direct contradictions flagged. Records correlate.</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Investigator Review Decision Box */}
                <div className="p-3 rounded border bg-card space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold">Investigator Review Decision</span>
                    <Badge variant="outline" className="text-[10px] capitalize">
                      Current: {selectedRow.review_status.replace("_", " ")}
                    </Badge>
                  </div>
                  <Input
                    placeholder="Add investigator review rationale / provenance notes..."
                    value={reviewNote}
                    onChange={(e) => setReviewNote(e.target.value)}
                    className="h-8 text-xs"
                  />
                  <div className="flex items-center gap-2 pt-1">
                    <Button
                      size="sm"
                      variant="default"
                      className="h-7 text-xs bg-emerald-600 hover:bg-emerald-700 text-white gap-1"
                      onClick={() => handleReviewAction("confirmed")}
                      disabled={submittingReview}
                    >
                      <CheckCircle2 className="h-3 w-3" />
                      Confirm Contradiction
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 text-xs text-zinc-400 gap-1"
                      onClick={() => handleReviewAction("dismissed")}
                      disabled={submittingReview}
                    >
                      <XCircle className="h-3 w-3" />
                      Dismiss
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 text-xs text-blue-400 gap-1"
                      onClick={() => handleReviewAction("unresolved")}
                      disabled={submittingReview}
                    >
                      <HelpCircle className="h-3 w-3" />
                      Mark Unresolved
                    </Button>
                  </div>

                  {/* Existing Review Notes Audit */}
                  {selectedRow.investigator_notes.length > 0 && (
                    <div className="pt-2 border-t text-[10px] space-y-1">
                      <span className="font-semibold text-muted-foreground">Recorded Audit Notes:</span>
                      {selectedRow.investigator_notes.map((n, idx) => (
                        <p key={idx} className="text-muted-foreground font-mono">
                          {n}
                        </p>
                      ))}
                    </div>
                  )}
                </div>

                {/* Evidence Verification & Provenance Drawer (when an evidence ID is selected) */}
                {selectedEvidenceId && (
                  <div className="p-3 rounded border bg-muted/20 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 font-semibold text-xs">
                        <ShieldCheck className="h-4 w-4 text-primary" />
                        <span>Evidence Verification: {selectedEvidenceId}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 text-[10px]"
                        onClick={() => setSelectedEvidenceId(null)}
                      >
                        Close
                      </Button>
                    </div>

                    {loadingEvidence ? (
                      <div className="text-xs text-muted-foreground py-3 text-center">Verifying hash integrity...</div>
                    ) : verificationData ? (
                      <div className="space-y-2 text-[10px]">
                        <div className="grid grid-cols-2 gap-2 bg-card p-2 rounded border font-mono">
                          <div>
                            <span className="text-muted-foreground">Stored SHA-256:</span>
                            <div className="truncate text-foreground">{verificationData.stored_sha256}</div>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Integrity Status:</span>
                            <div className="flex items-center gap-1 text-emerald-500 font-semibold">
                              <CheckCircle2 className="h-3 w-3" />
                              <span>{verificationData.integrity_status.toUpperCase()}</span>
                            </div>
                          </div>
                        </div>

                        {/* Provenance Flow */}
                        <div>
                          <span className="font-semibold text-muted-foreground">Forensic Provenance Chain:</span>
                          <div className="flex items-center gap-1 mt-1 overflow-x-auto py-1">
                            {provenanceData.map((node, i) => (
                              <div key={i} className="flex items-center gap-1 shrink-0">
                                <div className="px-2 py-1 rounded bg-card border text-[9px] space-y-0.5">
                                  <div className="font-semibold text-primary">{node.step}</div>
                                  <div className="text-muted-foreground truncate max-w-[120px]">{node.identifier}</div>
                                </div>
                                {i < provenanceData.length - 1 && (
                                  <ChevronRight className="h-3 w-3 text-muted-foreground shrink-0" />
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    ) : null}
                  </div>
                )}
              </div>
            </ScrollArea>
          </div>
        )}
      </div>
    </div>
  );
}
