"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, Shield } from "lucide-react";
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
import { useCreateCase } from "@/hooks/queries/useCases";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";
import { caseCreateSchema } from "@/features/cases/lib/validations";
import type { CaseOut } from "@/types/case";

type CaseCreateFormValues = {
  title: string;
  description?: string;
  priority?: "low" | "medium" | "high" | "critical";
};

interface CreateCaseDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onCreated?: (createdCase: CaseOut) => void;
}

export function CreateCaseDialog({
  open: externalOpen,
  onOpenChange: externalOnOpenChange,
  onCreated,
}: CreateCaseDialogProps = {}) {
  const [internalOpen, setInternalOpen] = useState(false);
  const isControlled = externalOpen !== undefined;
  const open = isControlled ? externalOpen : internalOpen;
  const setOpen = (val: boolean) => {
    if (isControlled && externalOnOpenChange) externalOnOpenChange(val);
    else setInternalOpen(val);
  };

  const createCase = useCreateCase();

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<CaseCreateFormValues>({
    resolver: zodResolver(caseCreateSchema),
    defaultValues: { title: "", description: "", priority: "medium" },
  });

  const priorityValue = watch("priority") ?? "medium";

  const onSubmit = async (data: CaseCreateFormValues) => {
    try {
      const created = await createCase.mutateAsync({
        title: data.title,
        description: data.description || null,
        priority: data.priority ?? "medium",
      });
      toast.add({
        title: "Case Created",
        description: `Case "${data.title}" has been created successfully.`,
        type: "success",
      });
      reset();
      setOpen(false);
      onCreated?.(created);
    } catch (error) {
      toast.add({
        title: "Failed to Create Case",
        description: getErrorMessage(error, "Could not create the case."),
        type: "error",
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {!isControlled && (
        <DialogTrigger
          render={
            <Button className="h-10 px-4 bg-[#164863] hover:bg-[#0F3550] text-white font-medium text-sm flex items-center gap-2 transition-colors cursor-pointer rounded-lg">
              <Plus className="h-4 w-4" />
              New Case
            </Button>
          }
        />
      )}
      {isControlled && (
        <Button
          onClick={() => setOpen(true)}
          className="h-10 px-4 bg-[#164863] hover:bg-[#0F3550] text-white font-medium text-sm flex items-center gap-2 transition-colors cursor-pointer rounded-lg"
        >
          <Plus className="h-4 w-4" />
          New Case
        </Button>
      )}
      <DialogContent className="sm:max-w-lg bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-xl shadow-xl text-gray-900 dark:text-white">
        <DialogHeader className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-blue-50 dark:bg-[#4F8CFF]/15 text-[#164863] dark:text-[#4F8CFF]">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-xl font-bold text-gray-900 dark:text-white">
                Open New Case
              </DialogTitle>
              <DialogDescription className="text-xs text-gray-500 dark:text-white/60">
                Initialize a forensic investigation case file across cluster nodes.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5 mt-4">
          <div className="space-y-2">
            <Label htmlFor="case-title" className="text-xs font-medium text-gray-600 dark:text-white/70 uppercase tracking-wider">
              Investigation Title *
            </Label>
            <Input
              id="case-title"
              placeholder="e.g., Incident #2026-9041 (Memory Injection)"
              {...register("title")}
              className="h-11 bg-gray-50 dark:bg-white/[0.04] border-gray-200 dark:border-white/10 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-white/30 rounded-lg focus:border-[#164863] dark:focus:border-[#4F8CFF]"
              aria-invalid={!!errors.title}
              aria-describedby={errors.title ? "title-error" : undefined}
            />
            {errors.title && (
              <p id="title-error" className="text-xs text-red-500 font-medium">
                {errors.title.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="case-description" className="text-xs font-medium text-gray-600 dark:text-white/70 uppercase tracking-wider">
              Description & Scope
            </Label>
            <Textarea
              id="case-description"
              placeholder="Provide context regarding affected hosts, suspicious artifacts, or compromised scope..."
              rows={4}
              {...register("description")}
              className="bg-gray-50 dark:bg-white/[0.04] border-gray-200 dark:border-white/10 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-white/30 rounded-lg focus:border-[#164863] dark:focus:border-[#4F8CFF]"
              aria-invalid={!!errors.description}
              aria-describedby={errors.description ? "description-error" : undefined}
            />
            {errors.description && (
              <p id="description-error" className="text-xs text-red-500 font-medium">
                {errors.description.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label className="text-xs font-medium text-gray-600 dark:text-white/70 uppercase tracking-wider">
              Initial Priority
            </Label>
            <Select
              value={priorityValue}
              onValueChange={(val) => {
                if (val)
                  setValue("priority", val as CaseCreateFormValues["priority"], {
                    shouldValidate: true,
                  });
              }}
            >
              <SelectTrigger className="w-full h-11 bg-gray-50 dark:bg-white/[0.04] border-gray-200 dark:border-white/10 text-gray-900 dark:text-white rounded-lg">
                <SelectValue placeholder="Select priority level" />
              </SelectTrigger>
              <SelectPositioner>
                <SelectPopup className="bg-white dark:bg-[#0F1115] border-gray-200 dark:border-white/10 text-gray-900 dark:text-white rounded-lg">
                  <SelectItem value="low">Low Priority</SelectItem>
                  <SelectItem value="medium">Medium Priority</SelectItem>
                  <SelectItem value="high">High Priority</SelectItem>
                  <SelectItem value="critical">Critical (Immediate Escalation)</SelectItem>
                </SelectPopup>
              </SelectPositioner>
            </Select>
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
              disabled={createCase.isPending}
              className="h-10 px-6 rounded-lg bg-[#164863] hover:bg-[#0F3550] dark:bg-[#4F8CFF] dark:hover:bg-[#3B72E6] text-white font-medium transition-colors"
            >
              {createCase.isPending ? "Initializing..." : "Create Investigation Case"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
