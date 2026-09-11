import { z } from "zod";

export const evidenceUploadSchema = z.object({
  case_id: z.string().optional().or(z.literal("")),
});

export const custodyAppendSchema = z.object({
  action: z.enum(["transfer", "access", "update", "review"]).default("transfer"),
  previous_owner: z.string().max(255).optional().or(z.literal("")),
  new_owner: z.string().max(255).optional().or(z.literal("")),
  location: z.string().max(255).optional().or(z.literal("")),
  notes: z.string().max(2000).optional().or(z.literal("")),
  signature: z.string().max(255).optional().or(z.literal("")),
});

export type EvidenceUploadFormData = z.infer<typeof evidenceUploadSchema>;
export type CustodyAppendFormData = z.infer<typeof custodyAppendSchema>;
