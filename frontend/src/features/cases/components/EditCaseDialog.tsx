"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Pencil, FileEdit } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectItem,
  SelectPopup,
  SelectPositioner,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useUpdateCase } from "@/hooks/queries/useCases";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";
import {
  caseUpdateSchema,
  type CaseUpdateFormData,
} from "@/features/cases/lib/validations";
import type { CaseOut } from "@/types/case";

const STATUS_OPTIONS = [
  { value: "open", label: "Open Investigation" },
  { value: "review", label: "In Review" },
  { value: "closed", label: "Closed & Resolved" },
];

const PRIORITY_OPTIONS = [
  { value: "low", label: "Low Priority" },
  { value: "medium", label: "Medium Priority" },
  { value: "high", label: "High Priority" },
  { value: "critical", label: "Critical Escalation" },
];

interface EditCaseDialogProps {
  caseItem: CaseOut;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function EditCaseDialog({ caseItem, open: controlledOpen, onOpenChange: controlledOnOpenChange }: EditCaseDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen ?? internalOpen;
  const setOpen = controlledOnOpenChange ?? setInternalOpen;
  const updateCase = useUpdateCase();

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<CaseUpdateFormData>({
    resolver: zodResolver(caseUpdateSchema),
    defaultValues: {
      title: caseItem.title,
      description: caseItem.description ?? "",
      status: caseItem.status ?? "open",
      priority: (caseItem.priority as CaseUpdateFormData["priority"]) ?? "medium",
      assigned_to: caseItem.assigned_to ?? null,
    },
  });

  useEffect(() => {
    if (open) {
      reset({
        title: caseItem.title,
        description: caseItem.description ?? "",
        status: caseItem.status ?? "open",
        priority: (caseItem.priority as CaseUpdateFormData["priority"]) ?? "medium",
        assigned_to: caseItem.assigned_to ?? null,
      });
    }
  }, [open, caseItem, reset]);

  const onSubmit = async (data: CaseUpdateFormData) => {
    try {
      await updateCase.mutateAsync({
        id: caseItem.id,
        payload: {
          title: data.title,
          description: data.description || null,
          status: data.status,
          priority: data.priority,
          assigned_to: data.assigned_to,
        },
      });
      toast.add({
        title: "Case Updated",
        description: `Case "${data.title}" details have been updated.`,
        type: "success",
      });
      setOpen(false);
    } catch (error) {
      toast.add({
        title: "Failed to Update Case",
        description: getErrorMessage(error, "Could not update the case."),
        type: "error",
      });
    }
  };

  const statusValue = watch("status") ?? "open";
  const priorityValue = watch("priority") ?? "medium";

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={
          <button
            className="w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/70 hover:text-white hover:bg-white/15 hover:border-white/25 transition-all"
            title="Edit Case Details"
          >
            <Pencil className="h-4 w-4" />
          </button>
        }
      />
      <DialogContent className="sm:max-w-lg p-6 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-xl shadow-xl text-gray-900 dark:text-white">
        <DialogHeader className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-blue-50 dark:bg-[#4F8CFF]/15 text-[#164863] dark:text-[#4F8CFF]">
              <FileEdit className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-xl font-bold text-gray-900 dark:text-white">
                Edit Case Metadata
              </DialogTitle>
              <DialogDescription className="text-xs text-gray-500 dark:text-white/60">
                Modify investigation title, description, status, or priority.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mt-3">
          <div className="space-y-2">
            <Label htmlFor="edit-title" className="text-xs font-medium text-gray-600 dark:text-white/70 uppercase tracking-wider">
              Title *
            </Label>
            <Input
              id="edit-title"
              {...register("title")}
              className="h-11 bg-gray-50 dark:bg-white/[0.04] border-gray-200 dark:border-white/10 text-gray-900 dark:text-white rounded-lg focus:border-[#164863] dark:focus:border-[#4F8CFF]"
              aria-invalid={!!errors.title}
              aria-describedby={errors.title ? "edit-title-error" : undefined}
            />
            {errors.title && (
              <p id="edit-title-error" className="text-xs text-red-500 font-medium">
                {errors.title.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-description" className="text-xs font-medium text-gray-600 dark:text-white/70 uppercase tracking-wider">
              Description & Findings
            </Label>
            <Textarea
              id="edit-description"
              rows={4}
              {...register("description")}
              className="bg-gray-50 dark:bg-white/[0.04] border-gray-200 dark:border-white/10 text-gray-900 dark:text-white rounded-lg focus:border-[#164863] dark:focus:border-[#4F8CFF]"
              aria-invalid={!!errors.description}
              aria-describedby={errors.description ? "edit-description-error" : undefined}
            />
            {errors.description && (
              <p id="edit-description-error" className="text-xs text-red-500 font-medium">
                {errors.description.message}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="edit-status" className="text-xs font-medium text-gray-600 dark:text-white/70 uppercase tracking-wider">
                Status
              </Label>
              <Select
                value={statusValue}
                onValueChange={(val) => {
                  if (val) setValue("status", val);
                }}
              >
                <SelectTrigger id="edit-status" className="h-11 bg-gray-50 dark:bg-white/[0.04] border-gray-200 dark:border-white/10 text-gray-900 dark:text-white rounded-lg">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectPositioner>
                  <SelectPopup className="bg-white dark:bg-[#0F1115] border-gray-200 dark:border-white/10 text-gray-900 dark:text-white rounded-lg">
                    {STATUS_OPTIONS.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectPopup>
                </SelectPositioner>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-priority" className="text-xs font-medium text-gray-600 dark:text-white/70 uppercase tracking-wider">
                Priority
              </Label>
              <Select
                value={priorityValue}
                onValueChange={(val) => {
                  if (val)
                    setValue("priority", val as CaseUpdateFormData["priority"], {
                      shouldValidate: true,
                    });
                }}
              >
                <SelectTrigger id="edit-priority" className="h-11 bg-gray-50 dark:bg-white/[0.04] border-gray-200 dark:border-white/10 text-gray-900 dark:text-white rounded-lg">
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectPositioner>
                  <SelectPopup className="bg-white dark:bg-[#0F1115] border-gray-200 dark:border-white/10 text-gray-900 dark:text-white rounded-lg">
                    {PRIORITY_OPTIONS.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectPopup>
                </SelectPositioner>
              </Select>
            </div>
          </div>

          <DialogFooter className="pt-4 border-t border-gray-100 dark:border-white/10 flex items-center justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              className="h-10 px-4 rounded-lg border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 text-gray-700 dark:text-white/80 hover:bg-gray-50 dark:hover:bg-white/10"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={updateCase.isPending}
              className="h-10 px-6 rounded-lg bg-[#164863] hover:bg-[#0F3550] dark:bg-[#4F8CFF] dark:hover:bg-[#3B72E6] text-white font-medium transition-colors"
            >
              {updateCase.isPending ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
