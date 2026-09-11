import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Users, MapPin, Smartphone, Building, FileText, Globe, Cpu, Shield, Clock, Database } from "lucide-react";

const TYPE_CONFIG: Record<string, { icon: typeof Users; color: string; bg: string }> = {
  person: { icon: Users, color: "text-blue-600", bg: "bg-blue-100 border-blue-300" },
  location: { icon: MapPin, color: "text-green-600", bg: "bg-green-100 border-green-300" },
  device: { icon: Smartphone, color: "text-purple-600", bg: "bg-purple-100 border-purple-300" },
  organization: { icon: Building, color: "text-orange-600", bg: "bg-orange-100 border-orange-300" },
  evidence: { icon: FileText, color: "text-emerald-600", bg: "bg-emerald-100 border-emerald-300" },
  url: { icon: Globe, color: "text-cyan-600", bg: "bg-cyan-100 border-cyan-300" },
  process: { icon: Cpu, color: "text-indigo-600", bg: "bg-indigo-100 border-indigo-300" },
  case: { icon: Shield, color: "text-amber-600", bg: "bg-amber-100 border-amber-300" },
  timeline: { icon: Clock, color: "text-pink-600", bg: "bg-pink-100 border-pink-300" },
  entity: { icon: Database, color: "text-gray-600", bg: "bg-gray-100 border-gray-300" },
};

const DEFAULT_CONFIG = TYPE_CONFIG.entity;

interface GraphNodeData {
  label: string;
  type?: string;
  isSelected?: boolean;
  properties?: Record<string, unknown>;
}

function GraphNodeComponent({ data, selected }: NodeProps & { data: GraphNodeData }) {
  const nodeType = (data.type ?? "entity").toLowerCase();
  const config = TYPE_CONFIG[nodeType] ?? DEFAULT_CONFIG;
  const Icon = config.icon;

  return (
    <div
      className={`relative flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border-2 shadow-sm transition-all cursor-pointer ${
        selected ? "ring-2 ring-primary ring-offset-1 " : ""
      }${config.bg}`}
    >
      <Handle type="target" position={Position.Left} className="!w-2 !h-2 !bg-muted-foreground" />
      <Icon className={`h-3.5 w-3.5 shrink-0 ${config.color}`} />
      <span className="text-[10px] font-medium truncate max-w-[100px]" title={data.label}>
        {data.label}
      </span>
      <Handle type="source" position={Position.Right} className="!w-2 !h-2 !bg-muted-foreground" />
    </div>
  );
}

export const CustomGraphNode = memo(GraphNodeComponent);
