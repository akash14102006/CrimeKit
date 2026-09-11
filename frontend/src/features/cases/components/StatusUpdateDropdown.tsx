"use client";

import { ChevronDown, Check } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useUpdateCase } from "@/hooks/queries/useCases";
import { toast } from "@/components/ui/toast";
import { getErrorMessage } from "@/lib/api-client";
import type { CaseOut } from "@/types/case";

const STATUS_CONFIG: Record<
  string,
  { label: string; dot: string; bg: string; text: string; border: string }
> = {
  open: {
    label: "Open",
    dot: "bg-emerald-400",
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    border: "border-emerald-500/30",
  },
  review: {
    label: "In Review",
    dot: "bg-amber-400",
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    border: "border-amber-500/30",
  },
  closed: {
    label: "Closed",
    dot: "bg-white/40",
    bg: "bg-white/10",
    text: "text-white/70",
    border: "border-white/15",
  },
};

interface StatusUpdateDropdownProps {
  caseItem: CaseOut;
}

export function StatusUpdateDropdown({ caseItem }: StatusUpdateDropdownProps) {
  const updateCase = useUpdateCase();
  const currentStatus = caseItem.status ?? "open";
  const config = STATUS_CONFIG[currentStatus] ?? STATUS_CONFIG.open;

  const handleStatusChange = async (newStatus: string) => {
    if (newStatus === currentStatus) return;
    try {
      await updateCase.mutateAsync({
        id: caseItem.id,
        payload: { status: newStatus },
      });
      toast.add({
        title: "Status Updated",
        description: `Case status changed to "${newStatus}".`,
        type: "success",
      });
    } catch (error) {
      toast.add({
        title: "Failed to Update Status",
        description: getErrorMessage(error, "Could not update case status."),
        type: "error",
      });
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <button className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-all cursor-pointer ${config.bg} ${config.text} ${config.border}`}>
            <span className={`h-2 w-2 rounded-full ${config.dot}`} />
            <span>{config.label}</span>
            <ChevronDown className="h-3 w-3 opacity-60 ml-0.5" />
          </button>
        }
      />
      <DropdownMenuContent align="start" className="w-44 p-1 bg-[#0F1115] border-white/15 rounded-xl shadow-xl text-white">
        {Object.entries(STATUS_CONFIG).map(([key, item]) => {
          const isCurrent = key === currentStatus;
          return (
            <DropdownMenuItem
              key={key}
              onClick={() => handleStatusChange(key)}
              className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium cursor-pointer transition-colors ${
                isCurrent ? "bg-white/15 text-white font-semibold" : "text-white/70 hover:bg-white/10 hover:text-white"
              }`}
            >
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${item.dot}`} />
                <span>{item.label}</span>
              </div>
              {isCurrent && <Check className="h-3.5 w-3.5 text-[#4F8CFF]" />}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
