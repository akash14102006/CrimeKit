import { z } from "zod";

export const caseCreateSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(255, "Title must be 255 characters or less"),
  description: z
    .string()
    .max(5000, "Description must be 5000 characters or less")
    .optional()
    .or(z.literal("")),
  priority: z.enum(["low", "medium", "high", "critical"]).default("medium"),
});

export const caseUpdateSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(255, "Title must be 255 characters or less")
    .optional(),
  description: z
    .string()
    .max(5000, "Description must be 5000 characters or less")
    .optional()
    .or(z.literal("")),
  status: z.string().optional(),
  priority: z.enum(["low", "medium", "high", "critical"]).optional(),
  assigned_to: z.string().nullable().optional(),
});

export type CaseCreateFormData = z.infer<typeof caseCreateSchema>;
export type CaseUpdateFormData = z.infer<typeof caseUpdateSchema>;
